#!/usr/bin/env python
import click
import json
import sys

from settings.settings import get_param
from settings.settings import init
from tools.logging_helper import init_logger
from tools.db import commit
from tools.db import get_cursor
from tools.db import rollback
from tools.rabbit import consume
from tools.rabbit import publish
from core.state import state
from core.state import set_item_state
from contracting_process import processor


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
        input_message = json.loads(body.decode('utf8'))

        dataset_id = input_message["dataset_id"]
        item_id = input_message["item_id"]

        logger.info("Processing message for dataset {} and item {}".format(dataset_id, item_id))

        processor.do_work(item_id)

        set_item_state(dataset_id, item_id, state.OK)

        message = """{{"item_id": "{}", "dataset_id":"{}"}}""".format(item_id, dataset_id)

        publish(message, get_param("exchange_name") + routing_key)
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
