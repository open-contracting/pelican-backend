#!/usr/bin/env python
import sys

import click
import simplejson as json

from core.state import get_dataset, get_processed_items_count, get_total_items_count, phase, set_dataset_state, state
from dataset import processor
from tools.bootstrap import bootstrap
from tools.db import commit
from tools.logging_helper import get_logger
from tools.rabbit import ack, consume, publish

consume_routing_key = "contracting_process_checker"

routing_key = "dataset_checker"


@click.command()
def start():
    """
    Perform the dataset-level checks.
    """
    init_worker()

    consume(callback, consume_routing_key)

    return


def callback(connection, channel, delivery_tag, body):
    try:
        # parse input message
        input_message = json.loads(body.decode("utf8"))
        dataset_id = input_message["dataset_id"]
        dataset = get_dataset(dataset_id)

        # optimization when resending
        if dataset["state"] == state.OK and dataset["phase"] == phase.DATASET:
            logger.info("Checks have been already calculated for this dataset.")
            ack(connection, channel, delivery_tag)
            return

        if dataset["state"] == state.IN_PROGRESS and dataset["phase"] == phase.DATASET:
            # lets do nothing, calculations is already in progress
            logger.info("Other worker probably already started with the job. Doing nothing.")
            ack(connection, channel, delivery_tag)
            return

        if dataset["phase"] == phase.TIME_VARIANCE or dataset["phase"] == phase.CHECKED:
            logger.info("Checks have been already calculated for this dataset.")
            ack(connection, channel, delivery_tag)
            return

        if dataset["state"] == state.IN_PROGRESS and dataset["phase"] == phase.CONTRACTING_PROCESS:
            # contracting process is not done yet
            logger.info("Not all messages have been processed by contracting process.")
            ack(connection, channel, delivery_tag)
            return

        processed_count = get_processed_items_count(dataset_id)
        total_count = get_total_items_count(dataset_id)

        # check whether are all items alredy processed
        if processed_count < total_count:
            # contracting process is not done yet
            logger.debug(
                "There are {} remaining messages to be processed for dataset_id {}".format(
                    total_count - processed_count, dataset_id
                )
            )

            logger.info("Not all messages have been processed by contracting process.")
            ack(connection, channel, delivery_tag)
            return

        if (
            dataset["state"] == state.OK
            and dataset["phase"] == phase.CONTRACTING_PROCESS
            and processed_count == total_count
        ):
            # set state to processing
            logger.info(
                f"All messages for dataset_id {dataset_id} with {processed_count} items processed, "
                "starting to calculate dataset level checks"
            )
            set_dataset_state(dataset_id, state.IN_PROGRESS, phase.DATASET)

            commit()

            # calculate all the stuff
            processor.do_work(dataset_id, logger)

            # mark dataset as done
            set_dataset_state(dataset_id, state.OK, phase.DATASET)

            commit()

            logger.info("Dataset level checks calculated for dataset_id {}.".format(dataset_id))

            # send message for a next phase
            message = {"dataset_id": dataset_id}
            publish(connection, channel, json.dumps(message), routing_key)

        else:
            logger.exception(
                "Dataset processing for dataset_id {} is in weird state. \
                Dataset state {}. Dataset phase {}.".format(
                    dataset_id, dataset["state"], dataset["phase"]
                )
            )
            sys.exit()

        ack(connection, channel, delivery_tag)
    except Exception:
        logger.exception("Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker():
    bootstrap("checker.dataset")

    global logger
    logger = get_logger()

    logger.debug("Dataset checker started.")


if __name__ == "__main__":
    start()
