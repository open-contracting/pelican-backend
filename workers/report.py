#!/usr/bin/env python
import logging

import click

import contracting_process.field_level.report_examples as field_level_report_examples
import contracting_process.resource_level.examples as resource_level_examples
import contracting_process.resource_level.report as resource_level_report
from dataset import meta_data_aggregator
from pelican.util import settings
from pelican.util.services import consume, phase
from pelican.util.workers import finish_callback, is_step_required

consume_routing_key = "time_variance_checker"
logger = logging.getLogger("pelican.workers.report")


@click.command()
def start():
    """
    Create reports, pick examples, and update dataset metadata.
    """
    consume(
        on_message_callback=callback,
        queue=consume_routing_key,
        # 3 hours in milliseconds.
        # https://www.rabbitmq.com/consumers.html
        arguments={"x-consumer-timeout": 3 * 60 * 60 * 1000},
    )


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    if is_step_required(settings.Steps.REPORT):
        logger.info("Dataset %s: Calculating compiled release-level check report", dataset_id)
        resource_level_report.create(dataset_id)

        logger.info("Dataset %s: Calculating compiled release-level check examples", dataset_id)
        resource_level_examples.create(dataset_id)

        logger.info("Dataset %s: Calculating field-level check report and examples", dataset_id)
        field_level_report_examples.create(dataset_id)

        logger.info("Dataset %s: Updating with Pelican metadata", dataset_id)
        meta_data = meta_data_aggregator.get_pelican_meta_data(dataset_id)
        meta_data_aggregator.update_meta_data(meta_data, dataset_id)

    finish_callback(client_state, channel, method, dataset_id, phase=phase.CHECKED)


if __name__ == "__main__":
    start()
