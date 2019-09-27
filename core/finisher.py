#!/usr/bin/env python
import click
import simplejson as json
import sys
from datetime import datetime

from dataset import meta_data_aggregator
from settings.settings import get_param
from tools.logging_helper import get_logger
from tools.db import commit
from tools.db import get_cursor
from tools.db import rollback
from tools.rabbit import consume
from tools.rabbit import publish
from core.state import state
from core.state import phase
from core.state import set_dataset_state
from core.state import get_processed_items_count
from core.state import get_total_items_count
from core.state import get_dataset
from time_variance import processor
from tools.bootstrap import bootstrap
import contracting_process.field_level.report as field_level_report
import contracting_process.resource_level.report as resource_level_report
import contracting_process.field_level.examples as field_level_examples
import contracting_process.resource_level.examples as resource_level_examples

import contracting_process.field_level.report_examples as field_level_report_examples

consume_routing_key = "_time_variance_checker"


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)

    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


def callback(channel, method, properties, body):
    try:
        # read and parse message
        input_message = json.loads(body.decode('utf8'))
        dataset_id = input_message["dataset_id"]

        # creating reports and examples
        logger.info("Resource level checks report for dataset_id {} is being calculated".format(dataset_id))
        resource_level_report.create(dataset_id)

        logger.info("Resource level checks examples for dataset_id {} are being picked".format(dataset_id))
        resource_level_examples.create(dataset_id)

        logger.info("Field level checks report for dataset_id {} is being calculated and \
            examples are being picked".format(dataset_id))
        field_level_report_examples.create(dataset_id)

        # adding final meta data for current dataset
        logger.info("Saving processing info to dataset table.")
        meta_data = meta_data_aggregator.get_dqt_meta_data(dataset_id)
        meta_data_aggregator.update_meta_data(meta_data, dataset_id)

        # mark dataset as beeing finished
        set_dataset_state(dataset_id, state.OK, phase.CHECKED)
        logger.info("All the work done for dataset_id {}".format(dataset_id))
        commit()

        # perform finish actions
        # send mails etc.

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(
            "Something went wrong when processing {}".format(body))
        sys.exit()


def init_worker(environment):
    bootstrap(environment, "finisher_worker")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.debug("Finisher worker started.")


if __name__ == '__main__':
    start()
