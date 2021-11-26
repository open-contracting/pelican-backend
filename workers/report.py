#!/usr/bin/env python
import click
from yapw.methods.blocking import ack

import contracting_process.field_level.report_examples as field_level_report_examples
import contracting_process.resource_level.examples as resource_level_examples
import contracting_process.resource_level.report as resource_level_report
from dataset import meta_data_aggregator
from tools.bootstrap import bootstrap
from tools.db import commit
from tools.logging_helper import get_logger
from tools.rabbit import create_client
from tools.state import phase, set_dataset_state, state

consume_routing_key = "time_variance_checker"


@click.command()
def start():
    """
    Create reports, pick examples, and update dataset metadata.
    """
    bootstrap("workers.report")

    global logger
    logger = get_logger()

    logger.debug("Finisher worker started.")

    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    # creating reports and examples
    logger.info("Resource level checks report for dataset_id %s is being calculated", dataset_id)
    resource_level_report.create(dataset_id)

    logger.info("Resource level checks examples for dataset_id %s are being picked", dataset_id)
    resource_level_examples.create(dataset_id)

    logger.info(
        "Field level checks report for dataset_id %s is being calculated and examples are being picked", dataset_id
    )
    field_level_report_examples.create(dataset_id)

    # adding final meta data for current dataset
    logger.info("Saving processing info to dataset table.")
    meta_data = meta_data_aggregator.get_dqt_meta_data(dataset_id)
    meta_data_aggregator.update_meta_data(meta_data, dataset_id)

    # mark dataset as beeing finished
    set_dataset_state(dataset_id, state.OK, phase.CHECKED)
    logger.info("All the work done for dataset_id %s", dataset_id)
    commit()

    ack(client_state, channel, method.delivery_tag)


if __name__ == "__main__":
    start()
