#!/usr/bin/env python
import click

from settings.settings import get_param
from settings.settings import init
from tools.logging_helper import init_logger
from tools.db import commit
from tools.db import get_cursor
from tools.db import rollback
from tools.rabbit import consume
from tools.rabbit import publish

consume_routing_key = "_ocds_kingfisher_extractor"

routing_key = "_contracting_process"


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    try:
        logger.info("Crawling of sreality started.")
        publish(message, get_param("exchange_name") + routing_key)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        sys.exit()
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    init(environment)

    global logger
    logger = init_logger("contracting_process_checker")

    global cursor
    cursor = get_cursor()

    logger.debug("Tender level worker initialised")


if __name__ == '__main__':
    start()
