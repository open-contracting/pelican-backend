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
from core.state import phase
from core.state import set_dataset_state
from core.state import get_processed_items_count
from core.state import get_total_items_count
from core.state import get_dataset
from time_variance import processor


consume_routing_key = "_time_variance_checker"


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    try:
        # read and parse message
        input_message = json.loads(body.decode('utf8'))
        dataset_id = input_message["dataset_id"]

        # mark dataset as beeing finished
        set_dataset_state(dataset_id, state.OK, phase.DONE)
        logger.info("All the work done for {}".format(dataset_id))

        # perform finish actions
        # send mails etc.

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    init(environment)

    global logger
    logger = init_logger("finisher_worker")

    global cursor
    cursor = get_cursor()

    logger.debug("Finisher worker started.")


if __name__ == '__main__':
    start()
