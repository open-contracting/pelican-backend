#!/usr/bin/env python
from math import ceil

import click
import psycopg2.extras
import simplejson as json

import dataset.meta_data_aggregator as meta_data_aggregator
from tools import exchange_rates_db, settings
from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor
from tools.logging_helper import get_logger
from tools.rabbit import ack, consume, publish
from tools.state import phase, set_dataset_state, set_item_state, state

consume_routing_key = "ocds_kingfisher_extractor_init"

routing_key = "extractor"

page_size = 1000

logger = None


@click.command()
def start():
    """
    Import collections from Kingfisher Process.
    """
    init_worker()

    if settings.FIXER_IO_API_KEY:
        exchange_rates_db.update_from_fixer_io()

    consume(callback, consume_routing_key)


def callback(connection, channel, delivery_tag, body):
    if settings.FIXER_IO_API_KEY:
        exchange_rates_db.update_from_fixer_io()
    cursor = get_cursor()
    try:
        input_message = json.loads(body.decode("utf8"))

        if "command" not in input_message:
            name = input_message["name"]
            collection_id = input_message["collection_id"]
            max_items = int(input_message["max_items"]) if "max_items" in input_message else None
            ancestor_id = int(input_message["ancestor_id"]) if "ancestor_id" in input_message else None

            logger.info("Reading kingfisher data started. name: %s collection_id: %s", name, collection_id)

            kf_connection = psycopg2.connect(settings.KINGFISHER_PROCESS_DATABASE_URL)

            kf_cursor = kf_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            logger.info("King fisher DB connection established")

            if max_items is None:
                kf_cursor.execute(
                    """
                    SELECT compiled_release.data_id
                    FROM compiled_release
                    JOIN data
                    ON compiled_release.data_id = data.id
                    WHERE compiled_release.collection_id = %s
                    AND pg_column_size(data.data) < %s;
                    """,
                    (collection_id, settings.KINGFISHER_PROCESS_MAX_SIZE),
                )
            else:
                kf_cursor.execute(
                    """
                    SELECT compiled_release.data_id
                    FROM compiled_release
                    JOIN data
                    ON compiled_release.data_id = data.id
                    WHERE compiled_release.collection_id = %s
                    AND pg_column_size(data.data) < %s
                    LIMIT %s;
                    """,
                    (collection_id, settings.KINGFISHER_PROCESS_MAX_SIZE, max_items),
                )

            result = kf_cursor.fetchall()

            logger.info("Creating row in dataset table for incoming collection")
            cursor.execute(
                """
                INSERT INTO dataset
                (name, meta, ancestor_id)
                VALUES
                (%s, %s, %s) RETURNING id;
                """,
                (name, json.dumps({}), ancestor_id),
            )
            dataset_id = cursor.fetchone()[0]

            logger.info("Saving meta data for dataset_id %s", dataset_id)
            meta_data = meta_data_aggregator.get_kingfisher_meta_data(collection_id)
            meta_data_aggregator.update_meta_data(meta_data, dataset_id)

            commit()

            # ack message, no recovery possible after this point
            ack(connection, channel, delivery_tag)

            # batch initialization
            max_batch_size = settings.EXTRACTOR_MAX_BATCH_SIZE
            batch_size = 0
            batch = []

            i = 0
            items_inserted = 0
            items_count = len(result)
            while i * page_size < items_count:
                ids = []
                for item in result[i * page_size : (i + 1) * page_size]:
                    ids.append(item[0])

                i += 1

                kf_cursor.execute(
                    """
                    SELECT data
                    FROM data
                    WHERE data.id IN %s;
                    """,
                    (tuple(ids),),
                )

                data_items = [(json.dumps(row[0]), dataset_id) for row in kf_cursor.fetchall()]
                sql = """
                    INSERT INTO data_item
                    (data, dataset_id)
                    VALUES %s
                    RETURNING id;
                """
                psycopg2.extras.execute_values(cursor, sql, data_items, page_size=page_size)
                commit()

                for row in cursor.fetchall():
                    inserted_id = row[0]

                    items_inserted += 1

                    set_item_state(dataset_id, inserted_id, state.IN_PROGRESS)

                    set_dataset_state(dataset_id, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=items_inserted)

                    if items_inserted == items_count:
                        set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS)

                    commit()

                    batch_size += 1
                    batch.append(inserted_id)
                    if batch_size >= max_batch_size or items_inserted == items_count:
                        message = {"item_ids": batch, "dataset_id": dataset_id}
                        publish(connection, channel, json.dumps(message), routing_key)

                        batch_size = 0
                        batch.clear()

                logger.info(
                    "Inserted page %s from %s. %s items out of %s downloaded",
                    i,
                    ceil(float(items_count) / float(page_size)),
                    items_inserted,
                    items_count,
                )

            logger.info("All items with dataset_id %s have been downloaded", dataset_id)
            kf_cursor.close()
            kf_connection.close()
        else:
            # resend messages
            dataset_id = input_message["dataset_id"]
            resend(connection, channel, dataset_id)
            ack(connection, channel, delivery_tag)
    except Exception:
        logger.exception("Something went wrong when processing %s", body)
        ack(connection, channel, delivery_tag)
    finally:
        cursor.close()


def resend(connection, channel, dataset_id):
    cursor = get_cursor()
    logger.info("Resending messages for dataset_id %s started", dataset_id)
    cursor.execute(
        """
            SELECT id FROM data_item
            WHERE dataset_id = %s
        """,
        (dataset_id,),
    )

    ids = cursor.fetchall()

    set_dataset_state(dataset_id, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=len(ids))

    # batch initialization
    max_batch_size = settings.EXTRACTOR_MAX_BATCH_SIZE
    batch_size = 0
    batch = []

    items_inserted = 0
    items_count = len(ids)
    for entry in ids:
        set_item_state(dataset_id, entry[0], state.IN_PROGRESS)
        items_inserted += 1
        if items_inserted == items_count:
            set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS)

        commit()

        batch_size += 1
        batch.append(entry[0])
        if batch_size >= max_batch_size or items_inserted == items_count:
            message = {"item_ids": batch, "dataset_id": dataset_id}
            publish(connection, channel, json.dumps(message), routing_key)

            batch_size = 0
            batch.clear()

    cursor.close()
    logger.info("Resending messages for dataset_id %s completed", dataset_id)


def init_worker():
    bootstrap("workers.extract.kingfisher_process")

    global logger
    logger = get_logger()

    logger.debug("OCDS Kingfisher extractor initialized.")


if __name__ == "__main__":
    start()
