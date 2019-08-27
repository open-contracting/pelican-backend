#!/usr/bin/env python
import simplejson as json
import sys
from datetime import datetime

import click
import psycopg2.extras

from core.state import phase, set_dataset_state, set_item_state, state
from settings.settings import get_param, init
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger
from tools.rabbit import consume, publish
from tools.bootstrap import bootstrap


consume_routing_key = "_ocds_kingfisher_extractor_init"

routing_key = "_ocds_kingfisher_extractor"

page_size = 1000

logger = None

cursor = None


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    try:
        input_message = json.loads(body.decode('utf8'))

        dataset_id = input_message["dataset_id"]

        if "command" not in input_message:
            collection_id = input_message["collection_id"]

            logger.info(
                "Reading kingfisher data started. Dataset: {} processing_id: {}".format(
                    input_message["dataset_id"],
                    dataset_id))

            kf_connection = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}' port ='{}'".format(
                get_param("kf_extractor_host"),
                get_param("kf_extractor_db"),
                get_param("kf_extractor_user"),
                get_param("kf_extractor_password"),
                get_param("kf_extractor_port")))

            kf_cursor = kf_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            logger.info("King fisher DB connection established")

            kf_cursor.execute("""
                SELECT compiled_release.data_id
                FROM collection
                INNER JOIN collection_file ON collection_file.collection_id = collection.id
                INNER JOIN collection_file_item ON collection_file_item.collection_file_id = collection_file.id
                INNER JOIN compiled_release ON compiled_release.collection_file_item_id = collection_file_item.id
                WHERE collection.id = %s;
                """, (collection_id,))

            result = kf_cursor.fetchall()

            i = 0
            items_inserted = 0
            while i * page_size < len(result):
                ids = []
                for item in result[i * page_size:(i + 1) * page_size]:
                    ids.append(item[0])

                i = i + 1

                kf_cursor.execute("""
                    SELECT data
                    FROM data
                    WHERE data.id IN %s;
                    """, (tuple(ids),))

                data = kf_cursor.fetchall()

                for data_item in data:
                    cursor.execute("""
                        INSERT INTO data_item
                        (data, dataset_id, created, modified)
                        VALUES
                        (%s, %s, now(), now()) RETURNING id
                    """, (json.dumps(data_item[0]), dataset_id))

                    inserted_id = cursor.fetchone()[0]

                    items_inserted = items_inserted + 1

                    set_item_state(dataset_id, inserted_id, state.IN_PROGRESS)

                    set_dataset_state(dataset_id, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=items_inserted)

                    commit()

                    message = """{{"item_id": "{}", "dataset_id":"{}"}}""".format(inserted_id, dataset_id)
                    publish(message, get_param("exchange_name") + routing_key)

                logger.info("Inserted page {} from {}".format(i, len(result)))
        else:
            # resend messages
            resend(dataset_id)

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def resend(dataset_id):
    logger.info("Resending messages for {} started".format(dataset_id))
    cursor.execute("""
            SELECT id FROM data_item
            WHERE dataset_id = %s
        """, (dataset_id,))

    ids = cursor.fetchall()

    items_inserted = 0
    for entry in ids:
        message = """{{"item_id": "{}", "dataset_id":"{}"}}""".format(entry[0], dataset_id)

        set_item_state(dataset_id, entry[0], state.IN_PROGRESS)
        items_inserted = items_inserted + 1
        set_dataset_state(dataset_id, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=len(ids))

        commit()

        publish(message, get_param("exchange_name") + routing_key)

    logger.info("Resending messages for {} completed".format(dataset_id))


def init_worker(environment):
    bootstrap(environment, "ocds_kingfisher_extractor")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.debug("OCDS Kingfisher extractor initialized.")


if __name__ == '__main__':
    start()
