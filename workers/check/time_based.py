#!/usr/bin/env python
import click

from time_variance import processor
from tools import settings
from tools.helpers import finish_worker, is_step_required
from tools.services import commit, create_client
from tools.state import phase, set_dataset_state, state

consume_routing_key = "dataset_checker"
routing_key = "time_variance_checker"


@click.command()
def start():
    """
    Perform the time-based checks.
    """
    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    if is_step_required(settings.Steps.TIME_BASED):
        set_dataset_state(dataset_id, state.IN_PROGRESS, phase.TIME_VARIANCE)
        commit()

        processor.do_work(dataset_id)

    finish_worker(client_state, channel, method, dataset_id, phase.TIME_VARIANCE, routing_key=routing_key)


if __name__ == "__main__":
    start()
