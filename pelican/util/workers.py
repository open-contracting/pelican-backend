import logging
from collections.abc import Callable
from functools import cache
from math import ceil
from typing import Any

import pika
from yapw.methods import ack, publish
from yapw.types import State as ClientState

from pelican.util import settings
from pelican.util.services import (
    Phase,
    State,
    commit,
    initialize_dataset_state,
    initialize_items_state,
    update_dataset_state,
)

logger = logging.getLogger(__name__)


@cache
def is_step_required(*steps: str) -> bool:
    """
    Return whether to run the step(s).

    :param: one or more steps

    .. seealso::

       :class:`pelican.util.settings.Steps`
    """
    return any(step in settings.STEPS for step in steps)


def process_items(
    client_state: ClientState,
    channel: pika.channel.Channel,
    method: pika.spec.Basic.Deliver,
    routing_key: str,
    cursors: dict[str, Any],
    dataset_id: int,
    ids: list[int],
    insert_items: Callable[[dict[str, Any], int, list[int]], None],
) -> None:
    """
    Load items into Pelican.

    Ack the message, initialize the dataset's and items' progress, insert items into the database in batches, and
    publish messages to process the items in batches.

    :param routing_key: the routing key for the outgoing message
    :param cursors: the database cursors ("default" is required)
    :param dataset_id: the dataset's ID
    :param ids: the ID's of rows to import
    :param insert_items: a function to insert the items, taking ``cursors``, ``dataset_id``, ``ids``
    """
    # Acknowledge early when using the Splitter pattern.
    ack(client_state, channel, method.delivery_tag)

    initialize_dataset_state(dataset_id)

    items_inserted = 0

    for page_number, i in enumerate(range(0, len(ids), settings.EXTRACTOR_PAGE_SIZE)):
        insert_items(cursors, dataset_id, ids[i : i + settings.EXTRACTOR_PAGE_SIZE])
        commit()

        # insert_items() returns the id's of the rows inserted into the data_item table.
        item_ids = [row[0] for row in cursors["default"]]
        for j in range(0, len(item_ids), settings.EXTRACTOR_MAX_BATCH_SIZE):
            item_ids_batch = item_ids[j : j + settings.EXTRACTOR_MAX_BATCH_SIZE]
            items_inserted += len(item_ids_batch)

            initialize_items_state(dataset_id, item_ids_batch)
            dataset_state = State.OK if items_inserted >= len(ids) else State.IN_PROGRESS
            update_dataset_state(dataset_id, Phase.CONTRACTING_PROCESS, dataset_state, size=items_inserted)
            commit()

            publish(client_state, channel, {"item_ids": item_ids_batch, "dataset_id": dataset_id}, routing_key)

        logger.info(
            "Dataset %s: Inserted %s/%s pages (%s/%s items)",
            dataset_id,
            page_number + 1,
            ceil(len(ids) / settings.EXTRACTOR_PAGE_SIZE),
            items_inserted,
            len(ids),
        )


def finish_callback(
    client_state: ClientState,
    channel: pika.channel.Channel,
    method: pika.spec.Basic.Deliver,
    dataset_id: int,
    phase: str | None = None,
    routing_key: str | None = None,
) -> None:
    """
    Update the dataset's state, publish a message if a routing key is provided, and ack the message.

    :param dataset_id: the dataset's ID
    :param phase: the dataset's phase
    :param routing_key: the routing key for the outgoing message
    """
    if phase:
        update_dataset_state(dataset_id, phase, State.OK)
    commit()
    if routing_key:
        publish(client_state, channel, {"dataset_id": dataset_id}, routing_key)
    ack(client_state, channel, method.delivery_tag)
