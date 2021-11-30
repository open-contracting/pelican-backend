#!/usr/bin/env python
import logging

import click
from yapw.methods.blocking import ack, nack, publish

from dataset import processor
from tools import settings
from tools.currency_converter import bootstrap
from tools.helpers import is_step_required
from tools.services import commit, create_client
from tools.state import (
    get_dataset_progress,
    get_processed_items_count,
    get_total_items_count,
    phase,
    set_dataset_state,
    state,
)

consume_routing_key = "contracting_process_checker"
routing_key = "dataset_checker"
logger = logging.getLogger("pelican.workers.check.dataset")


@click.command()
def start():
    """
    Perform the dataset-level checks.
    """
    bootstrap()
    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    if not is_step_required(settings.DATASET_STEP):
        # send message for a next phase
        message = {"dataset_id": dataset_id}
        publish(client_state, channel, message, routing_key)
        return

    delivery_tag = method.delivery_tag

    dataset = get_dataset_progress(dataset_id)

    # optimization when resending
    if dataset["state"] == state.OK and dataset["phase"] == phase.DATASET:
        logger.info("Checks have been already calculated for this dataset.")
        ack(client_state, channel, delivery_tag)
        return

    if dataset["state"] == state.IN_PROGRESS and dataset["phase"] == phase.DATASET:
        # lets do nothing, calculations is already in progress
        logger.info("Other worker probably already started with the job. Doing nothing.")
        ack(client_state, channel, delivery_tag)
        return

    if dataset["phase"] == phase.TIME_VARIANCE or dataset["phase"] == phase.CHECKED:
        logger.info("Checks have been already calculated for this dataset.")
        ack(client_state, channel, delivery_tag)
        return

    if dataset["state"] == state.IN_PROGRESS and dataset["phase"] == phase.CONTRACTING_PROCESS:
        # contracting process is not done yet
        logger.info("Not all messages have been processed by contracting process.")
        ack(client_state, channel, delivery_tag)
        return

    processed_count = get_processed_items_count(dataset_id)
    total_count = get_total_items_count(dataset_id)

    # check whether are all items alredy processed
    if processed_count < total_count:
        # contracting process is not done yet
        logger.debug(
            "There are %s remaining messages to be processed for dataset_id %s",
            total_count - processed_count,
            dataset_id,
        )

        logger.info("Not all messages have been processed by contracting process.")
        ack(client_state, channel, delivery_tag)
        return

    if (
        dataset["state"] == state.OK
        and dataset["phase"] == phase.CONTRACTING_PROCESS
        and processed_count == total_count
    ):
        # set state to processing
        logger.info(
            "All messages for dataset_id %s with %s items processed, starting to calculate dataset level checks",
            dataset_id,
            processed_count,
        )
        set_dataset_state(dataset_id, state.IN_PROGRESS, phase.DATASET)

        commit()

        # calculate all the stuff
        processor.do_work(dataset_id, logger)

        # mark dataset as done
        set_dataset_state(dataset_id, state.OK, phase.DATASET)

        commit()

        logger.info("Dataset level checks calculated for dataset_id %s.", dataset_id)

        # send message for a next phase
        message = {"dataset_id": dataset_id}
        publish(client_state, channel, message, routing_key)

    else:
        logger.error(
            "Dataset processing for dataset_id %s is in weird state. Dataset state %s. Dataset phase %s.",
            dataset_id,
            dataset["state"],
            dataset["phase"],
        )
        nack(client_state, channel, delivery_tag, requeue=False)

    ack(client_state, channel, delivery_tag)


if __name__ == "__main__":
    start()
