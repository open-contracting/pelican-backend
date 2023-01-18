#!/usr/bin/env python
import logging

import click

import contracting_process.field_level.report_examples as field_level_report_examples
import contracting_process.resource_level.examples as resource_level_examples
import contracting_process.resource_level.report as resource_level_report
from dataset import meta_data_aggregator
from tools import settings
from tools.helpers import finish_callback, is_step_required
from tools.services import consume, phase

consume_routing_key = "time_variance_checker"
logger = logging.getLogger("pelican.workers.report")


@click.command()
def start():
    """
    Create reports, pick examples, and update dataset metadata.
    """
    consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    if is_step_required(settings.Steps.REPORT):
        logger.info("Calculating report for compiled release-level checks of dataset_id %s", dataset_id)
        resource_level_report.create(dataset_id)

        logger.info("Picking examples for compiled release-level checks of dataset_id %s", dataset_id)
        resource_level_examples.create(dataset_id)

        logger.info("Calculating report and picking examples for field-level checks of dataset_id %s", dataset_id)
        field_level_report_examples.create(dataset_id)

        logger.info("Saving Pelican metadata")
        meta_data = meta_data_aggregator.get_dqt_meta_data(dataset_id)
        meta_data_aggregator.update_meta_data(meta_data, dataset_id)

    finish_callback(client_state, channel, method, dataset_id, phase=phase.CHECKED)


if __name__ == "__main__":
    start()
