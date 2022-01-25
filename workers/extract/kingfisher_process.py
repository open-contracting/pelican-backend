#!/usr/bin/env python
import logging
from math import ceil

import click
import psycopg2.extras
import simplejson as json
from yapw.methods.blocking import ack, publish

import dataset.meta_data_aggregator as meta_data_aggregator
from tools import exchange_rates_db, settings
from tools.services import commit, consume, get_cursor
from tools.state import phase, set_dataset_state, set_items_state, state

consume_routing_key = "ocds_kingfisher_extractor_init"
routing_key = "extractor"
page_size = 1000
logger = logging.getLogger("pelican.workers.extract.kingfisher_process")


@click.command()
def start():
    """
    Import collections from Kingfisher Process.
    """
    consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    delivery_tag = method.delivery_tag
    if settings.FIXER_IO_API_KEY:
        exchange_rates_db.update_from_fixer_io()
    cursor = get_cursor()
    try:
        name = input_message["name"]
        collection_id = input_message["collection_id"]
        max_items = int(input_message["max_items"]) if "max_items" in input_message else None
        ancestor_id = int(input_message["ancestor_id"]) if "ancestor_id" in input_message else None

        kf_connection = psycopg2.connect(settings.KINGFISHER_PROCESS_DATABASE_URL)

        kf_cursor = kf_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        logger.info("Kingfisher Process database connection established.")

        if max_items is None:
            kf_cursor.execute(
                """\
                SELECT compiled_release.data_id
                FROM compiled_release
                JOIN data ON compiled_release.data_id = data.id
                WHERE
                    compiled_release.collection_id = %(collection_id)s
                    AND pg_column_size(data.data) < %(max_size)s
                """,
                {"collection_id": collection_id, "max_size": settings.KINGFISHER_PROCESS_MAX_SIZE},
            )
        else:
            kf_cursor.execute(
                """\
                SELECT compiled_release.data_id
                FROM compiled_release
                JOIN data ON compiled_release.data_id = data.id
                WHERE
                    compiled_release.collection_id = %(collection_id)s
                    AND pg_column_size(data.data) < %(max_size)s
                LIMIT %(limit)s
                """,
                {"collection_id": collection_id, "max_size": settings.KINGFISHER_PROCESS_MAX_SIZE, "limit": max_items},
            )

        result = kf_cursor.fetchall()

        logger.info("Creating row in dataset table for incoming collection")
        cursor.execute(
            """\
            INSERT INTO dataset (name, meta, ancestor_id)
            VALUES (%(name)s, %(meta)s, %(ancestor_id)s)
            RETURNING id
            """,
            {"name": name, "meta": json.dumps({}), "ancestor_id": ancestor_id},
        )
        dataset_id = cursor.fetchone()[0]

        logger.info("Saving meta data for dataset_id %s", dataset_id)
        meta_data = meta_data_aggregator.get_kingfisher_meta_data(collection_id)
        meta_data_aggregator.update_meta_data(meta_data, dataset_id)

        commit()

        # ack message, no recovery possible after this point
        ack(client_state, channel, delivery_tag)

        # batch initialization
        max_batch_size = settings.EXTRACTOR_MAX_BATCH_SIZE
        batch_size = 0
        batch = []

        i = 0
        inserts = 0
        items_count = len(result)
        while i * page_size < items_count:
            ids = []
            for item in result[i * page_size : (i + 1) * page_size]:
                ids.append(item[0])

            i += 1

            kf_cursor.execute("SELECT data FROM data WHERE data.id IN %(ids)s", {"ids": tuple(ids)})

            data_items = [(json.dumps(row[0]), dataset_id) for row in kf_cursor.fetchall()]
            sql = "INSERT INTO data_item (data, dataset_id) VALUES %s RETURNING id"
            psycopg2.extras.execute_values(cursor, sql, data_items, page_size=page_size)
            commit()

            for row in cursor.fetchall():
                inserted_id = row[0]
                batch.append(inserted_id)
                batch_size += 1
                inserts += 1

                if batch_size >= max_batch_size or inserts == items_count:
                    set_items_state(dataset_id, batch, state.IN_PROGRESS)

                    if inserts == items_count:
                        set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS, size=inserts)
                    else:
                        set_dataset_state(dataset_id, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=inserts)

                    commit()

                    publish(client_state, channel, {"item_ids": batch, "dataset_id": dataset_id}, routing_key)

                    batch_size = 0
                    batch.clear()

            logger.info(
                "Inserted page %s from %s. %s items out of %s downloaded",
                i,
                ceil(float(items_count) / float(page_size)),
                inserts,
                items_count,
            )

        logger.info("Done extracting data to dataset %s", dataset_id)
        kf_cursor.close()
        kf_connection.close()
    finally:
        cursor.close()


if __name__ == "__main__":
    start()
