#!/usr/bin/env python
import os
import shutil
import tempfile
import time

import click
import requests
import shortuuid
import simplejson as json

from core.state import get_dataset, get_processed_items_count, get_total_items_count, phase, set_dataset_state, state
from settings.settings import get_param
from time_variance import processor
from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger
from tools.rabbit import consume, publish


@click.command()
@click.argument("environment")
@click.argument("name")
@click.argument("collection_id")
@click.option("--ancestor_id", default=None, help="Id of already calculated dataset. Used for time variance checks.")
@click.option("--max_items", default=None, help="Number of items to be downloaded. USefull for testing and debug.")
def start(environment, name, collection_id, ancestor_id, max_items):
    init_worker(environment)

    logger.info("Updating registries...")
    with open("registry/origin.json", "r") as json_file:
        origin = json.load(json_file)

    for path, urls in origin.items():
        logger.info("Updating registry on path %s" % path)
        update_registry(path, urls)

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


def update_registry(path, urls, file_format="csv"):
    tempdir = tempfile.mkdtemp()
    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            logger.warning("File at %s could not be downloaded" % url)
            continue

        with open(os.path.join(tempdir, shortuuid.uuid()), "wb") as file:
            file.write(response.content)

        logger.info("File at %s was successfully downloaded; sleeping for 2 seconds" % url)
        time.sleep(2)

    logger.info("Joining all the files...")
    if file_format == "csv":
        with open(path, "w") as registry_file:
            for index, file_name in enumerate(os.listdir(tempdir)):
                with open(os.path.join(tempdir, file_name), "r") as file:
                    if index != 0:
                        file.__next__()
                    for line in file:
                        registry_file.write(line)
    else:
        shutil.rmtree(tempdir)
        raise ValueError("File format '%s' is not supported" % file_format)

    shutil.rmtree(tempdir)


if __name__ == "__main__":
    start()
