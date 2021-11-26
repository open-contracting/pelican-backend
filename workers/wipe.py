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
    bootstrap("workers.wipe")

    global logger
    logger = get_logger()

    logger.debug("Wiper worker started.")

    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]
    logger.info("All the data for dataset_id %s will removed", dataset_id)

    with get_cursor() as cursor:
        cursor.execute(
            """
                DELETE FROM field_level_check WHERE dataset_id = %(id)s;
                DELETE FROM field_level_check_examples WHERE dataset_id IN %(id)s;
                DELETE FROM resource_level_check WHERE dataset_id = %(id)s;
                DELETE FROM resource_level_check_examples WHERE dataset_id IN %(id)s;
                DELETE FROM report WHERE dataset_id IN %(id)s;
                DELETE FROM dataset_level_check WHERE dataset_id IN %(id)s;
                DELETE FROM time_variance_level_check WHERE dataset_id IN %(id)s;
                DELETE FROM progress_monitor_item WHERE dataset_id = %(id)s;
                DELETE FROM progress_monitor_dataset WHERE dataset_id = %(id)s;
                DELETE FROM data_item WHERE dataset_id = %(id)s;
                DELETE FROM dataset WHERE id = %(id)s;
            """,
            {"id": dataset_id},
        )

    commit()
    ack(client_state, channel, method.delivery_tag)


if __name__ == "__main__":
    start()
