#!/usr/bin/env python
import json
import sys

import click

from contracting_process import processor
from core.state import set_item_state, state
from settings.settings import get_param, init
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import init_logger
from tools.rabbit import consume, publish

consume_routing_key = "_ocds_kingfisher_extractor"

routing_key = "_contracting_process_checker"


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    try:
        # parse input message
        input_message = json.loads(body.decode('utf8'))
        dataset_id = input_message["dataset_id"]
        item_id = input_message["item_id"]

        logger.info("Processing message for dataset {} and item {}".format(dataset_id, item_id))

        # get item from storage
        cursor.execute("""
            SELECT data
            FROM data_item
            WHERE id = %s;
            """, (int(item_id),))

        item = cursor.fetchone()[0]

        # perform actual action with the item
        processor.do_work(item)

        # set state of processed item
        set_item_state(dataset_id, item_id, state.OK)

        # send message to next phase
        message = """{{"item_id": "{}", "dataset_id":"{}"}}""".format(item_id, dataset_id)
        publish(message, get_param("exchange_name") + routing_key)

        # acknowledge message processing
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    init(environment)

    global logger
    logger = init_logger("contracting_process_checker")

    global cursor
    cursor = get_cursor()

    logger.info("Contracting process checker initialised")


if __name__ == '__main__':
    start()
