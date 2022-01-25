#!/usr/bin/env python
import click
from yapw.methods.blocking import ack

from tools.services import commit, consume, get_cursor

consume_routing_key = "wiper_init"


@click.command()
def start():
    """
    Delete datasets.
    """
    consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    with get_cursor() as cursor:
        cursor.execute(
            """\
            DELETE FROM field_level_check WHERE dataset_id = %(dataset_id)s;
            DELETE FROM field_level_check_examples WHERE dataset_id = %(dataset_id)s;
            DELETE FROM resource_level_check WHERE dataset_id = %(dataset_id)s;
            DELETE FROM resource_level_check_examples WHERE dataset_id = %(dataset_id)s;
            DELETE FROM report WHERE dataset_id = %(dataset_id)s;
            DELETE FROM dataset_level_check WHERE dataset_id = %(dataset_id)s;
            DELETE FROM time_variance_level_check WHERE dataset_id = %(dataset_id)s;
            DELETE FROM progress_monitor_item WHERE dataset_id = %(dataset_id)s;
            DELETE FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s;
            DELETE FROM data_item WHERE dataset_id = %(dataset_id)s;
            DELETE FROM dataset WHERE id = %(dataset_id)s;
            """,
            {"dataset_id": dataset_id},
        )

    commit()

    ack(client_state, channel, method.delivery_tag)


if __name__ == "__main__":
    start()
