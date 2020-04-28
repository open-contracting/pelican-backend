#!/usr/bin/env python
import simplejson as json
import sys

import click

from core.state import phase, set_dataset_state, set_item_state, state
from settings.settings import get_param
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger
from tools.rabbit import consume, publish
from tools.bootstrap import bootstrap
from contracting_process import processor

consume_routing_key = "_extractor"

routing_key = "_contracting_process_checker"


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    try:
        # parse input message
        input_message = json.loads(body.decode('utf8'))
        dataset_id = input_message["dataset_id"]

        if "command" not in input_message:
            item_ids = input_message["item_ids"]

            logger.info("Processing message for dataset_id {} and items {}".format(dataset_id, item_ids))

            # get item from storage
            cursor.execute("""
                SELECT data, id, dataset_id
                FROM data_item
                WHERE id IN %s;
                """, (tuple(item_ids),))

            # perform actual action with items
            processor.do_work(cursor.fetchall())

            commit()

            # send message to next phase
            message = {"dataset_id": dataset_id}
            publish(json.dumps(message), get_param("exchange_name") + routing_key)
        else:
            resend(dataset_id)
        # acknowledge message processing
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()

    logger.info("Processing completed.")


def resend(dataset_id):
    logger.info("Resending messages for dataset_id {} started".format(dataset_id))

    # mark dataset as done
    set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS)

    commit()

    message = {"dataset_id": dataset_id}
    publish(json.dumps(message), get_param("exchange_name") + routing_key)

    logger.info("Resending messages for dataset_id {} completed".format(dataset_id))


def init_worker(environment):
    bootstrap(environment, "contracting_process_checker")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.info("Contracting process checker initialised")


if __name__ == '__main__':
    start()
