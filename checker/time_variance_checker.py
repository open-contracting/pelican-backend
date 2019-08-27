#!/usr/bin/env python
import simplejson as json
import sys
from datetime import datetime

import click

from core.state import (get_dataset, get_processed_items_count,
                        get_total_items_count, phase, set_dataset_state, state)
from settings.settings import get_param
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger
from tools.rabbit import consume, publish
from tools.bootstrap import bootstrap

consume_routing_key = "_dataset_checker"

routing_key = "_time_variance_checker"


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

        # mark dataset as beeing processed
        set_dataset_state(dataset_id, state.IN_PROGRESS, phase.TIME_VARIANCE)
        logger.info("Time variance level checks calculation started for {}".format(dataset_id))

        # do actual calculations
        processor.do_work(dataset_id)

        # all done, mark as completed
        set_dataset_state(dataset_id, state.OK, phase.TIME_VARIANCE)
        logger.info("Time variance level checks calculated for {}".format(dataset_id))

        # send messages into next phases
        message = """{{"dataset_id":"{}"}}""".format(dataset_id)
        publish(message, get_param("exchange_name") + routing_key)

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    bootstrap(environment, "time_variance_checker")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.debug("Time variance checker started.")

    global processor
    from time_variance import processor


if __name__ == '__main__':
    start()
