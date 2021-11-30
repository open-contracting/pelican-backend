#!/usr/bin/env python
import logging

import click
from yapw.methods.blocking import ack, publish

from contracting_process import processor
from tools import settings
from tools.currency_converter import bootstrap
from tools.helpers import is_step_required
from tools.services import commit, create_client, get_cursor
from tools.state import phase, set_dataset_state, state

consume_routing_key = "extractor"
routing_key = "contracting_process_checker"
logger = logging.getLogger("pelican.workers.check.data_item")


@click.command()
def start():
    """
    Perform the field-level and compiled release-level checks.
    """
    bootstrap()
    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    cursor = get_cursor()
    try:
        dataset_id = input_message["dataset_id"]

        if "command" not in input_message:
            item_ids = input_message["item_ids"]

            logger.info("Processing message for dataset_id %s and items %s", dataset_id, item_ids)

            # get item from storage
            cursor.execute(
                """
                SELECT data, id, dataset_id
                FROM data_item
                WHERE id IN %s;
                """,
                (tuple(item_ids),),
            )

            # perform actual action with items
            processor.do_work(cursor.fetchall(), do_field_level_checks=is_step_required(settings.FIELD_COVERAGE_STEP),
                              do_resource_level_checks=is_step_required(settings.FIELD_QUALITY_STEP))

            commit()

            # send message to next phase
            message = {"dataset_id": dataset_id}
            publish(client_state, channel, message, routing_key)
        else:
            resend(client_state, channel, dataset_id)
        ack(client_state, channel, method.delivery_tag)
    finally:
        cursor.close()

    logger.info("Processing completed.")


def resend(client_state, channel, dataset_id):
    logger.info("Resending messages for dataset_id %s started", dataset_id)

    # mark dataset as done
    set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS)

    commit()

    message = {"dataset_id": dataset_id}
    publish(client_state, channel, message, routing_key)

    logger.info("Resending messages for dataset_id %s completed", dataset_id)


if __name__ == "__main__":
    start()
