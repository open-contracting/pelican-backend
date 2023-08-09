#!/usr/bin/env python
import logging

import click
from yapw.methods import ack, nack

from dataset import processor
from pelican.util import settings
from pelican.util.currency_converter import bootstrap
from pelican.util.services import (
    commit,
    consume,
    get_dataset_progress,
    get_processed_items_count,
    get_total_items_count,
    phase,
    state,
    update_dataset_state,
)
from pelican.util.workers import finish_callback, is_step_required

consume_routing_key = "contracting_process_checker"
routing_key = "dataset_checker"
logger = logging.getLogger("pelican.workers.check.dataset")


@click.command()
def start():
    """
    Perform the dataset-level checks.
    """
    bootstrap()
    consume(on_message_callback=callback, queue=consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    delivery_tag = method.delivery_tag

    dataset_id = input_message["dataset_id"]
    dataset = get_dataset_progress(dataset_id)

    if dataset["phase"] == phase.CONTRACTING_PROCESS and dataset["state"] == state.IN_PROGRESS:
        logger.info("CONTRACTING_PROCESS phase still in-progress for dataset_id %s", dataset_id)
        ack(client_state, channel, delivery_tag)
        return
    if dataset["phase"] == phase.DATASET and dataset["state"] == state.IN_PROGRESS:
        logger.info("DATASET phase already in-progress for dataset_id %s", dataset_id)
        ack(client_state, channel, delivery_tag)
        return
    if dataset["phase"] in (phase.DATASET, phase.TIME_VARIANCE, phase.CHECKED, phase.DELETED):
        logger.info("DATASET phase already complete for dataset_id %s", dataset_id)
        ack(client_state, channel, delivery_tag)
        return

    # Implement the Aggregator pattern.
    processed_count = get_processed_items_count(dataset_id)
    total_count = get_total_items_count(dataset_id)
    difference = total_count - processed_count

    if difference:
        logger.info("CONTRACTING_PROCESS phase has %s messages left for dataset_id %s", difference, dataset_id)
        ack(client_state, channel, delivery_tag)
        return

    if not is_step_required(settings.Steps.DATASET):
        finish_callback(client_state, channel, method, dataset_id, phase=phase.DATASET, routing_key=routing_key)
        return

    if dataset["phase"] == phase.CONTRACTING_PROCESS and dataset["state"] == state.OK and not difference:
        logger.info(
            "All messages for dataset_id %s with %s items processed, starting to calculate dataset level checks",
            dataset_id,
            processed_count,
        )
        update_dataset_state(dataset_id, phase.DATASET, state.IN_PROGRESS)
        commit()

        processor.do_work(dataset_id)

        finish_callback(client_state, channel, method, dataset_id, phase=phase.DATASET, routing_key=routing_key)
    else:
        logger.error(
            "Dataset processing for dataset_id %s is in unexpected state (phase=%s, state=%s).",
            dataset_id,
            dataset["phase"],
            dataset["state"],
        )
        nack(client_state, channel, delivery_tag, requeue=False)


if __name__ == "__main__":
    start()
