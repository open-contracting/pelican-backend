#!/usr/bin/env python
import sys

import click
import simplejson as json

from settings.settings import get_param
from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor
from tools.logging_helper import get_logger
from tools.rabbit import ack, consume

consume_routing_key = "_wiper_init"


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(connection, channel, delivery_tag, body):
    try:
        # read and parse message
        input_message = json.loads(body.decode("utf8"))
        dataset_id = input_message["dataset_id"]

        # creating reports and examples
        logger.info("All the data for dataset_id {} will removed".format(dataset_id))

        cursor.execute("delete from resource_level_check where dataset_id = %s;", (tuple(dataset_id),))
        cursor.execute("delete from field_level_check where dataset_id = %s;", (tuple(dataset_id),))
        cursor.execute("delete from progress_monitor_item where dataset_id = %s;", (tuple(dataset_id),))
        cursor.execute("delete from progress_monitor_dataset where dataset_id = %s;", (tuple(dataset_id),))
        cursor.execute("delete from data_item where dataset_id = %s;", (tuple(dataset_id),))
        cursor.execute("delete from dataset where id = %s;", (tuple(dataset_id),))

        commit()

        ack(connection, channel, delivery_tag)
    except Exception:
        logger.exception("Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    bootstrap(environment, "wiper_worker")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.debug("Wiper worker started.")


if __name__ == "__main__":
    start()
