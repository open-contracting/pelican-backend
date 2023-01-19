#!/usr/bin/env python
import click

from pelican.util import settings
from pelican.util.services import commit, consume, phase, state, update_dataset_state
from pelican.util.workers import finish_callback, is_step_required
from time_variance import processor

consume_routing_key = "dataset_checker"
routing_key = "time_variance_checker"


@click.command()
def start():
    """
    Perform the time-based checks.
    """
    consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    if is_step_required(settings.Steps.TIME_BASED):
        update_dataset_state(dataset_id, phase.TIME_VARIANCE, state.IN_PROGRESS)
        commit()

        processor.do_work(dataset_id)

    finish_callback(client_state, channel, method, dataset_id, phase=phase.TIME_VARIANCE, routing_key=routing_key)


if __name__ == "__main__":
    start()
