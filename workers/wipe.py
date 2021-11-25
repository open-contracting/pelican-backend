#!/usr/bin/env python
import click
from yapw.methods.blocking import ack

from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor
from tools.logging_helper import get_logger
from tools.rabbit import create_client

consume_routing_key = "wiper_init"


@click.command()
def start():
    """
    Delete datasets.
    """
    init_worker()

    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    cursor = get_cursor()
    try:
        dataset_id = input_message["dataset_id"]

        # creating reports and examples
        logger.info("All the data for dataset_id %s will removed", dataset_id)

        cursor.execute("delete from resource_level_check where dataset_id = %(id)s;", {"id": dataset_id})
        cursor.execute("delete from field_level_check where dataset_id = %(id)s;", {"id": dataset_id})
        cursor.execute("delete from progress_monitor_item where dataset_id = %(id)s;", {"id": dataset_id})
        cursor.execute("delete from progress_monitor_dataset where dataset_id = %(id)s;", {"id": dataset_id})
        cursor.execute("delete from data_item where dataset_id = %(id)s;", {"id": dataset_id})
        cursor.execute("delete from dataset where id = %(id)s;", {"id": dataset_id})

        commit()

        ack(client_state, channel, method.delivery_tag)
    finally:
        cursor.close()


def init_worker():
    bootstrap("workers.wipe")

    global logger
    logger = get_logger()

    logger.debug("Wiper worker started.")


if __name__ == "__main__":
    start()
