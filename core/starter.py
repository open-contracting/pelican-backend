#!/usr/bin/env python
import json
import sys
from datetime import datetime

import click

from core.state import (get_dataset, get_processed_items_count,
                        get_total_items_count, phase, set_dataset_state, state)
from settings.settings import get_param, init
from time_variance import processor
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import init_logger
from tools.rabbit import consume, publish


@click.command()
@click.argument("environment")
@click.argument("dataset_id")
def start(environment, dataset_id):
    init_worker(environment, dataset_id)

    routing_key = "_ocds_kingfisher_extractor_init"

    message = """{{"dataset_id":"{}"}}""".format(dataset_id)
    publish(message, get_param("exchange_name") + routing_key)

    return


def init_worker(environment):
    init(environment)

    global logger
    logger = init_logger("starter")

    global cursor
    cursor = get_cursor()

    logger.debug("Starter started:)")


if __name__ == '__main__':
    start()
