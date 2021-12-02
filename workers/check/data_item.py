#!/usr/bin/env python
import click
from yapw.methods.blocking import ack, publish

from contracting_process import processor
from tools import settings
from tools.currency_converter import bootstrap
from tools.helpers import is_step_required
from tools.services import commit, create_client, get_cursor

consume_routing_key = "extractor"
routing_key = "contracting_process_checker"


@click.command()
def start():
    """
    Perform the field-level and compiled release-level checks.
    """
    bootstrap()
    create_client().consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]
    item_ids = input_message["item_ids"]

    with get_cursor() as cursor:
        cursor.execute("SELECT data, id, dataset_id FROM data_item WHERE id IN %(ids)s", {"ids": tuple(item_ids)})

    processor.do_work(
        cursor.fetchall(),
        do_field_level_checks=is_step_required(settings.Steps.FIELD_COVERAGE, settings.Steps.FIELD_QUALITY),
        do_resource_level_checks=is_step_required(settings.Steps.COMPILED_RELEASE),
    )

    commit()

    publish(client_state, channel, {"dataset_id": dataset_id}, routing_key)

    ack(client_state, channel, method.delivery_tag)


if __name__ == "__main__":
    start()
