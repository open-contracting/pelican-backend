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
from dataset import processor


consume_routing_key = "_contracting_process_checker"

routing_key = "_dataset_checker"


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

        processed_count = get_processed_items_count(dataset_id)
        total_count = get_total_items_count(dataset_id)

        if processed_count < total_count:
            logger.debug("There are {} remaining messages to be processed for {}".format(
                total_count - processed_count, dataset_id))
        else:
            dataset = get_dataset(dataset_id)
            if dataset["state"] == state.IN_PROGRESS and dataset["phase"] == phase.CONTRACTING_PROCESS:
                logger.info("All messages for {} processed, starting to calculate dataset level checks".format(dataset_id))
                set_dataset_state(dataset_id, state.IN_PROGRESS, phase.DATASET)

                commit()

                processor.do_work(dataset_id)

                set_dataset_state(dataset_id, state.OK, phase.DATASET)

                logger.info("Dataset level checks calculated for {}.".format(dataset_id))

                commit()

                message = """{{"dataset_id":"{}"}}""".format(dataset_id)

                publish(message, get_param("exchange_name") + routing_key)
            else:
                logger.info("Probably other worker already started with the job. Doing nothing.")

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    init(environment)

    global logger
    logger = init_logger("dataset_checker")

    global cursor
    cursor = get_cursor()

    logger.debug("Dataset checker started.")


if __name__ == '__main__':
    start()
