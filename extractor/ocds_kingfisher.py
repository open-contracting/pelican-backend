#!/usr/bin/env python
import sys
from datetime import datetime
from math import ceil

import click
import psycopg2.extras
import simplejson as json

import dataset.meta_data_aggregator as meta_data_aggregator
from core.state import phase, set_dataset_state, set_item_state, state
from settings.settings import get_param
from tools import exchange_rates_db
from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger
from tools.rabbit import consume, publish

consume_routing_key = "_ocds_kingfisher_extractor_init"

routing_key = "_extractor"

page_size = 1000

logger = None

cursor = None


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    # fixer io update
    if get_param("fixer_io_update"):
        exchange_rates_db.update_from_fixer_io()

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    # fixer io update
    if get_param("fixer_io_update"):
        exchange_rates_db.update_from_fixer_io()

    try:
        input_message = json.loads(body.decode("utf8"))

        if "command" not in input_message:
            name = input_message["name"]
            collection_id = input_message["collection_id"]
            max_items = int(input_message["max_items"]) if input_message["max_items"] else None
            ancestor_id = int(input_message["ancestor_id"]) if input_message["ancestor_id"] else None

            logger.info("Reading kingfisher data started. name: {} collection_id: {}".format(name, collection_id))

            kf_connection = psycopg2.connect(
                "host='{}' dbname='{}' user='{}' password='{}' port ='{}'".format(
                    get_param("kf_extractor_host"),
                    get_param("kf_extractor_db"),
                    get_param("kf_extractor_user"),
                    get_param("kf_extractor_password"),
                    get_param("kf_extractor_port"),
                )
            )

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
                    (collection_id, get_param("kf_extractor_max_size")),
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
                    (collection_id, get_param("kf_extractor_max_size"), max_items),
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
            commit()

            logger.info("Saving meta data for dataset_id {}".format(dataset_id))
            meta_data = meta_data_aggregator.get_kingfisher_meta_data(collection_id)
            meta_data_aggregator.update_meta_data(meta_data, dataset_id)

            # batch initialization
            max_batch_size = get_param("extractor_max_batch_size")
            batch_size = 0
            batch = []

            i = 0
            items_inserted = 0
            items_count = len(result)
            while i * page_size < items_count:
                ids = []
                for item in result[i * page_size : (i + 1) * page_size]:
                    ids.append(item[0])

                i = i + 1

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

                    items_inserted = items_inserted + 1

                    set_item_state(dataset_id, inserted_id, state.IN_PROGRESS)

                    set_dataset_state(dataset_id, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=items_inserted)

                    if items_inserted == items_count:
                        set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS)

                    commit()

                    batch_size += 1
                    batch.append(inserted_id)
                    if batch_size >= max_batch_size or items_inserted == items_count:
                        message = {"item_ids": batch, "dataset_id": dataset_id}
                        publish(json.dumps(message), get_param("exchange_name") + routing_key)

                        batch_size = 0
                        batch.clear()

                logger.info(
                    "Inserted page {} from {}. {} items out of {} downloaded".format(
                        i, ceil(float(items_count) / float(page_size)), items_inserted, items_count
                    )
                )

            logger.info("All items with dataset_id {} have been downloaded".format(dataset_id))

        else:
            # resend messages
            dataset_id = input_message["dataset_id"]
            resend(dataset_id)

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception:
        logger.exception("Something went wrong when processing {}".format(body))
        sys.exit()


def resend(dataset_id):
    logger.info("Resending messages for dataset_id {} started".format(dataset_id))
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
    max_batch_size = get_param("extractor_max_batch_size")
    batch_size = 0
    batch = []

    items_inserted = 0
    items_count = len(ids)
    for entry in ids:
        set_item_state(dataset_id, entry[0], state.IN_PROGRESS)
        items_inserted = items_inserted + 1
        if items_inserted == items_count:
            set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS)

        commit()

        batch_size += 1
        batch.append(entry[0])
        if batch_size >= max_batch_size or items_inserted == items_count:
            message = {"item_ids": batch, "dataset_id": dataset_id}
            publish(json.dumps(message), get_param("exchange_name") + routing_key)

            batch_size = 0
            batch.clear()

    logger.info("Resending messages for dataset_id {} completed".format(dataset_id))


def init_worker(environment):
    bootstrap(environment, "ocds_kingfisher_extractor")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.debug("OCDS Kingfisher extractor initialized.")


if __name__ == "__main__":
    start()
