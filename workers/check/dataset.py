import logging

import click
from yapw.methods import ack, nack

from dataset import processor
from pelican.util import settings
from pelican.util.currency_converter import get_exchange_rates
from pelican.util.services import (
    Phase,
    State,
    claim_dataset_phase,
    consume,
    get_dataset_progress,
    get_processed_items_count,
    get_total_items_count,
)
from pelican.util.workers import finish_callback, is_step_required

consume_routing_key = "contracting_process_checker"
routing_key = "dataset_checker"
logger = logging.getLogger("pelican.workers.check.dataset")


@click.command()
def start():
    """Perform the dataset-level checks."""
    get_exchange_rates()
    consume(
        on_message_callback=callback,
        queue=consume_routing_key,
        prefetch_count=settings.DATASET_PREFETCH_COUNT,
        # The data item scan scales with dataset size, and misc.url_availability can wait up to REQUESTS_TIMEOUT
        # per sampled URL.
        arguments={"x-consumer-timeout": settings.RABBIT_CONSUMER_TIMEOUT},
    )


def callback(client_state, channel, method, properties, input_message):
    delivery_tag = method.delivery_tag

    dataset_id = input_message["dataset_id"]
    dataset = get_dataset_progress(dataset_id)

    if dataset["phase"] == Phase.CONTRACTING_PROCESS and dataset["state"] == State.IN_PROGRESS:
        logger.info("Dataset %s: CONTRACTING_PROCESS phase still in-progress", dataset_id)
        ack(client_state, channel, delivery_tag)
        return
    if dataset["phase"] == Phase.DATASET and dataset["state"] == State.IN_PROGRESS:
        logger.info("Dataset %s: DATASET phase already in-progress", dataset_id)
        ack(client_state, channel, delivery_tag)
        return
    if dataset["phase"] in {Phase.DATASET, Phase.TIME_VARIANCE, Phase.CHECKED, Phase.DELETED}:
        logger.info("Dataset %s: DATASET phase already complete", dataset_id)
        ack(client_state, channel, delivery_tag)
        return

    if dataset["phase"] != Phase.CONTRACTING_PROCESS or dataset["state"] != State.OK:
        logger.error(
            "Dataset %s is in an unexpected state (phase=%s, state=%s).",
            dataset_id,
            dataset["phase"],
            dataset["state"],
        )
        nack(client_state, channel, delivery_tag, requeue=False)
        return

    # Implement the Aggregator pattern.
    processed_count = get_processed_items_count(dataset_id)
    total_count = get_total_items_count(dataset_id)
    difference = total_count - processed_count

    if difference:
        logger.info("Dataset %s: CONTRACTING_PROCESS phase has %s items left", dataset_id, difference)
        ack(client_state, channel, delivery_tag)
        return

    # The guards above are not atomic with this update. Claim the dataset, in case messages for the same dataset are
    # processed concurrently.
    if not claim_dataset_phase(dataset_id, Phase.CONTRACTING_PROCESS, State.OK, Phase.DATASET, State.IN_PROGRESS):
        logger.info("Dataset %s: DATASET phase already in-progress", dataset_id)
        ack(client_state, channel, delivery_tag)
        return

    if is_step_required(settings.Steps.DATASET):
        logger.info(
            "Dataset %s: Processed all %s items, starting dataset-level checks...", dataset_id, processed_count
        )
        processor.do_work(dataset_id)

    finish_callback(client_state, channel, method, dataset_id, phase=Phase.DATASET, routing_key=routing_key)


if __name__ == "__main__":
    start()
