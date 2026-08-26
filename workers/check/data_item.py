import click

from contracting_process import processor
from pelican.util import settings
from pelican.util.currency_converter import get_exchange_rates
from pelican.util.services import State, consume, execute
from pelican.util.workers import finish_callback

consume_routing_key = "extractor"
routing_key = "contracting_process_checker"


@click.command()
def start():
    """Perform the field-level and compiled release-level checks."""
    get_exchange_rates()
    consume(on_message_callback=callback, queue=consume_routing_key, prefetch_count=settings.DATA_ITEM_PREFETCH_COUNT)


def callback(client_state, channel, method, properties, input_message):
    dataset_id = input_message["dataset_id"]
    item_ids = input_message["item_ids"]

    if method.redelivered:
        # Skip items whose checks are already committed: a batch's check results and item states commit atomically,
        # which can occur before the message is acknowledged. The check tables have no unique constraint, so
        # duplicate rows would go unnoticed, and would skew the report's percentages.
        rows = execute(
            """\
            SELECT data_item.data, data_item.id
            FROM data_item
            JOIN progress_monitor_item
                ON progress_monitor_item.dataset_id = %(dataset_id)s AND progress_monitor_item.item_id = data_item.id
            WHERE data_item.id = ANY(%(ids)s) AND progress_monitor_item.state != %(state)s
            """,
            {"dataset_id": dataset_id, "ids": item_ids, "state": State.OK},
        )
    else:
        rows = execute("SELECT data, id FROM data_item WHERE id = ANY(%(ids)s)", {"ids": item_ids})

    processor.do_work(dataset_id, [(row["data"], row["id"]) for row in rows])

    finish_callback(client_state, channel, method, dataset_id, routing_key=routing_key)


if __name__ == "__main__":
    start()
