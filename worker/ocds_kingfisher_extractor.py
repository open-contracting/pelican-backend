#!/usr/bin/env python
import click
import json
import sys

from datetime import datetime
from settings.settings import get_param
from settings.settings import init
from tools.logging_helper import init_logger
from tools.db import commit
from tools.db import get_cursor
from tools.db import rollback
from tools.rabbit import consume
from tools.rabbit import publish
from core.state import state
from core.state import set_dataset_state
from core.state import set_item_state

consume_routing_key = "_ocds_kingfisher_extractor_init"

routing_key = "_ocds_kingfisher_extractor"


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    try:
        input_message = json.loads(body.decode('utf8'))

        dataset_id = input_message["dataset_id"] + "_" + datetime.now().strftime('%Y%m%d_%H%M%S')

        logger.info(
            "Reading kingfisher data started. Dataset: {} processing_id: {}".format(
                input_message["dataset_id"],
                dataset_id))

        set_dataset_state(dataset_id, state.IN_PROGRESS)

        for i in range(5, 8):

            item_id = i

            message = """{{"item_id": "{}", "dataset_id":"{}"}}""".format(item_id, dataset_id)

            set_item_state(dataset_id, item_id, state.IN_PROGRESS)

            publish(message, get_param("exchange_name") + routing_key)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    init(environment)

    global logger
    logger = init_logger("ocds_kingfisher_extractor")

    global cursor
    cursor = get_cursor()

    logger.debug("OCDS Kingfisher extractor initialized.")


if __name__ == '__main__':
    start()
