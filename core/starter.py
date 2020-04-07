#!/usr/bin/env python
import simplejson as json
import requests
import sys
from datetime import datetime

import click

from core.state import (get_dataset, get_processed_items_count,
                        get_total_items_count, phase, set_dataset_state, state)
from settings.settings import get_param
from time_variance import processor
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger
from tools.rabbit import consume, publish
from tools.bootstrap import bootstrap


@click.command()
@click.argument("environment")
@click.argument("name")
@click.argument("collection_id")
@click.option('--ancestor_id', default=None, help='Id of already calculated dataset. Used for time variance checks.')
@click.option("--max_items", default=None, help="Number of items to be downloaded. USefull for testing and debug.")
def start(environment, name, collection_id, ancestor_id, max_items):
    init_worker(environment)

    logger.info('Updating registries...')
    with open('registry/origin.json', 'r') as json_file:
        origin = json.load(json_file)

    for path, url in origin.items():
        response = requests.get(url)
        if response.status_code != 200:
            logger.info('%s file from %s could not be updated properly' % (path, url))
            continue

        with open(path, 'wb') as file:
            file.write(response.content)

        logger.info('%s file from %s has been updated.' % (path, url))

    routing_key = "_ocds_kingfisher_extractor_init"

    message = {
        "name": name,
        "collection_id": collection_id,
        "ancestor_id": ancestor_id,
        "max_items": max_items,
    }
    publish(json.dumps(message), get_param("exchange_name") + routing_key)

    return


def init_worker(environment):
    bootstrap(environment, "starter_worker")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.debug("Starter worker started.")


if __name__ == '__main__':
    start()
