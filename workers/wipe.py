import click
from yapw.methods import ack

from pelican.util.services import commit, consume, get_cursor

consume_routing_key = "wiper_init"


@click.command()
def start():
    """
    Delete datasets.
    """
    consume(on_message_callback=callback, queue=consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]

    with get_cursor() as cursor:
        parameters = {"dataset_id": dataset_id}
        cursor.execute("DELETE FROM field_level_check             WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM field_level_check_examples    WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM resource_level_check          WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM resource_level_check_examples WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM report                        WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM dataset_level_check           WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM time_variance_level_check     WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM progress_monitor_item         WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM progress_monitor_dataset      WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM data_item                     WHERE dataset_id = %(dataset_id)s", parameters)
        cursor.execute("DELETE FROM dataset                       WHERE id         = %(dataset_id)s", parameters)

    commit()

    ack(client_state, channel, method.delivery_tag)


if __name__ == "__main__":
    start()
