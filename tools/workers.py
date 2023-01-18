import logging
from math import ceil
from typing import Optional

from yapw.methods.blocking import ack, publish

from tools import settings
from tools.services import commit, initialize_dataset_state, initialize_items_state, phase, state, update_dataset_state

logger = logging.getLogger(__name__)


def is_step_required(*steps: str) -> bool:
    return any(step in settings.STEPS for step in steps)


def process_items(client_state, channel, method, routing_key, cursors, dataset_id, ids, insert_items):
    ack(client_state, channel, method.delivery_tag)

    initialize_dataset_state(dataset_id)

    items_inserted = 0

    for page_number, i in enumerate(range(0, len(ids), settings.EXTRACTOR_PAGE_SIZE)):
        insert_items(cursors, dataset_id, ids[i : i + settings.EXTRACTOR_PAGE_SIZE])
        commit()

        # insert_items() returns the id's of the rows inserted into the data_item table.
        item_ids = [row[0] for row in cursors["default"].fetchall()]
        for j in range(0, len(item_ids), settings.EXTRACTOR_MAX_BATCH_SIZE):
            item_ids_batch = item_ids[j : j + settings.EXTRACTOR_MAX_BATCH_SIZE]
            items_inserted += len(item_ids_batch)

            initialize_items_state(dataset_id, item_ids_batch, state.IN_PROGRESS)
            dataset_state = state.OK if items_inserted >= len(ids) else state.IN_PROGRESS
            update_dataset_state(dataset_id, phase.CONTRACTING_PROCESS, dataset_state, size=items_inserted)
            commit()

            publish(client_state, channel, {"item_ids": item_ids_batch, "dataset_id": dataset_id}, routing_key)

        logger.info(
            "Inserted %s/%s pages (%s/%s items) for dataset %s",
            page_number + 1,
            ceil(len(ids) / settings.EXTRACTOR_PAGE_SIZE),
            items_inserted,
            len(ids),
            dataset_id,
        )


def finish_callback(
    client_state, channel, method, dataset_id: int, phase: Optional[str] = None, routing_key: Optional[str] = None
) -> None:
    """
    Update the dataset's state, publish a message if a routing key is provided, and ack the message.
    """
    if phase:
        update_dataset_state(dataset_id, phase, state.OK)
    commit()
    if routing_key:
        publish(client_state, channel, {"dataset_id": dataset_id}, routing_key)
    ack(client_state, channel, method.delivery_tag)
