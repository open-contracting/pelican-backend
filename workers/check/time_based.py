#!/usr/bin/env python
import sys

import click
import simplejson as json

from time_variance import processor
from tools.bootstrap import bootstrap
from tools.db import commit
from tools.logging_helper import get_logger
from tools.rabbit import ack, consume, publish
from tools.state import phase, set_dataset_state, state

consume_routing_key = "dataset_checker"

routing_key = "time_variance_checker"


@click.command()
def start():
    """
    Perform the time-based checks.
    """
    init_worker()

    consume(callback, consume_routing_key)


def callback(connection, channel, delivery_tag, body):
    try:
        # read and parse message
        input_message = json.loads(body.decode("utf8"))
        dataset_id = input_message["dataset_id"]

        # mark dataset as beeing processed
        set_dataset_state(dataset_id, state.IN_PROGRESS, phase.TIME_VARIANCE)
        logger.info("Time variance level checks calculation started for dataset_id {}".format(dataset_id))
        commit()

        # do actual calculations
        processor.do_work(dataset_id)

        # all done, mark as completed
        set_dataset_state(dataset_id, state.OK, phase.TIME_VARIANCE)
        logger.info("Time variance level checks calculated for dataset_id {}".format(dataset_id))
        commit()

        # send messages into next phases
        message = {"dataset_id": dataset_id}
        publish(connection, channel, json.dumps(message), routing_key)

        ack(connection, channel, delivery_tag)
    except Exception:
        logger.exception("Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker():
    bootstrap("workers.check.time_based")

    global logger
    logger = get_logger()

    logger.debug("Time variance checker started.")


if __name__ == "__main__":
    start()