import logging

import click
from yapw.methods import ack

from pelican.util import settings
from pelican.util.services import SLOW_CONSUMER_ARGUMENTS, Phase, State, claim_dataset_phase, consume
from pelican.util.workers import finish_callback, is_step_required
from time_variance import processor

consume_routing_key = "dataset_checker"
routing_key = "time_variance_checker"
logger = logging.getLogger("pelican.workers.check.time_based")


@click.command()
def start():
    """Perform the time-based checks."""
    # Every data item of the ancestor dataset is processed.
    consume(on_message_callback=callback, queue=consume_routing_key, arguments=SLOW_CONSUMER_ARGUMENTS)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    # Claim the dataset, so that a redelivered message doesn't repeat the checks or publish again.
    if not claim_dataset_phase(dataset_id, Phase.DATASET, State.OK, Phase.TIME_VARIANCE, State.IN_PROGRESS):
        logger.info("Dataset %s: TIME_VARIANCE phase already in-progress", dataset_id)
        ack(client_state, channel, method.delivery_tag)
        return

    if is_step_required(settings.Steps.TIME_BASED):
        processor.do_work(dataset_id)

    finish_callback(client_state, channel, method, dataset_id, phase=Phase.TIME_VARIANCE, routing_key=routing_key)


if __name__ == "__main__":
    start()
