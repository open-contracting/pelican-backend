#!/usr/bin/env python
import logging

import click
from yapw.methods.blocking import ack, publish

from time_variance import processor
from tools import settings
from tools.helpers import is_step_required
from tools.services import commit, create_client
from tools.state import phase, set_dataset_state, state

consume_routing_key = "dataset_checker"
routing_key = "time_variance_checker"
logger = logging.getLogger("pelican.workers.check.time_based")


@click.command()
def start():
    """
    Perform the time-based checks.
    """
    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    if not is_step_required(settings.TIME_BASED_STEP):
        # send message for a next phase
        message = {"dataset_id": dataset_id}
        publish(client_state, channel, message, routing_key)
        return

    # mark dataset as beeing processed
    set_dataset_state(dataset_id, state.IN_PROGRESS, phase.TIME_VARIANCE)
    logger.info("Time variance level checks calculation started for dataset_id %s", dataset_id)
    commit()

    # do actual calculations
    processor.do_work(dataset_id)

    # all done, mark as completed
    set_dataset_state(dataset_id, state.OK, phase.TIME_VARIANCE)
    logger.info("Time variance level checks calculated for dataset_id %s", dataset_id)
    commit()

    # send messages into next phases
    message = {"dataset_id": dataset_id}
    publish(client_state, channel, message, routing_key)

    ack(client_state, channel, method.delivery_tag)


if __name__ == "__main__":
    start()
