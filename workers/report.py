#!/usr/bin/env python
import logging

import click

import contracting_process.field_level.report_examples as field_level_report_examples
import contracting_process.resource_level.examples as resource_level_examples
import contracting_process.resource_level.report as resource_level_report
from dataset import meta_data_aggregator
from tools import settings
from tools.helpers import finish_worker, is_step_required
from tools.services import create_client
from tools.state import phase

consume_routing_key = "time_variance_checker"
logger = logging.getLogger("pelican.workers.report")


@click.command()
def start():
    """
    Create reports, pick examples, and update dataset metadata.
    """
    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    if not is_step_required(settings.Steps.REPORT):
        finish_worker(client_state, channel, method, dataset_id, phase.CHECKED)
        return

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

    finish_worker(
        client_state,
        channel,
        method,
        dataset_id,
        phase.CHECKED,
        logger=logger,
        logger_message=f"All the work done for dataset_id {dataset_id}",
    )


if __name__ == "__main__":
    start()
