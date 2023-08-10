#!/usr/bin/env python
import multiprocessing

import click

from contracting_process import processor
from pelican.util.currency_converter import bootstrap
from pelican.util.services import consume, get_cursor
from pelican.util.workers import finish_callback

consume_routing_key = "extractor"
routing_key = "contracting_process_checker"


@click.command()
def start():
    """
    Perform the field-level and compiled release-level checks.
    """
    bootstrap()
    consume(on_message_callback=callback, queue=consume_routing_key, prefetch_count=multiprocessing.cpu_count())


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]
    item_ids = input_message["item_ids"]

    with get_cursor() as cursor:
        cursor.execute("SELECT data, id FROM data_item WHERE id = ANY(%(ids)s)", {"ids": item_ids})
        processor.do_work(dataset_id, cursor.fetchall())

    finish_callback(client_state, channel, method, dataset_id, routing_key=routing_key)


if __name__ == "__main__":
    start()
