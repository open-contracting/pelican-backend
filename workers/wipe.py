#!/usr/bin/env python
import sys

import click
import simplejson as json

from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor
from tools.logging_helper import get_logger
from tools.rabbit import ack, consume

consume_routing_key = "wiper_init"


@click.command()
def start():
    """
    Delete datasets.
    """
    init_worker()

    consume(callback, consume_routing_key)


def callback(connection, channel, delivery_tag, body):
    cursor = get_cursor()
    try:
        # read and parse message
        input_message = json.loads(body.decode("utf8"))
        dataset_id = input_message["dataset_id"]

        # creating reports and examples
        logger.info("All the data for dataset_id {} will removed".format(dataset_id))

        cursor.execute("delete from resource_level_check where dataset_id = %s;", (dataset_id,))
        cursor.execute("delete from field_level_check where dataset_id = %s;", (dataset_id,))
        cursor.execute("delete from progress_monitor_item where dataset_id = %s;", (dataset_id,))
        cursor.execute("delete from progress_monitor_dataset where dataset_id = %s;", (dataset_id,))
        cursor.execute("delete from data_item where dataset_id = %s;", (dataset_id,))
        cursor.execute("delete from dataset where id = %s;", (dataset_id,))

        commit()

        ack(connection, channel, delivery_tag)
    except Exception:
        logger.exception("Something went wrong when processing {}".format(body))
        sys.exit()
    finally:
        cursor.close()


def init_worker():
    bootstrap("workers.wipe")

    global logger
    logger = get_logger()

    logger.debug("Wiper worker started.")


if __name__ == "__main__":
    start()
