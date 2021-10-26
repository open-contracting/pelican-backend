#!/usr/bin/env python
import os
import shutil
import tempfile
import time

import click
import requests
import shortuuid
import simplejson as json

from tools.bootstrap import bootstrap
from tools.logging_helper import get_logger
from tools.rabbit import connect_and_publish_message


@click.command()
@click.argument("name")
@click.argument("collection_id")
@click.option("--previous-dataset", type=int, help="ID of previous dataset for time-based checks.")
@click.option("--sample", type=int, help="Number of compiled releases to import.")
def start(name, collection_id, previous_dataset, sample):
    """
    Create a dataset.
    """
    init_worker()

    logger.info("Updating registries...")
    with open("registry/origin.json", "r") as json_file:
        origin = json.load(json_file)

    for path, urls in origin.items():
        logger.info("Updating registry on path %s" % path)
        update_registry(path, urls)

    routing_key = "ocds_kingfisher_extractor_init"

    message = {
        "name": name,
        "collection_id": collection_id,
        "ancestor_id": previous_dataset,
        "max_items": sample,
    }
    connect_and_publish_message(json.dumps(message), routing_key)

    return


def init_worker():
    bootstrap("core.starter")

    global logger
    logger = get_logger()

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
