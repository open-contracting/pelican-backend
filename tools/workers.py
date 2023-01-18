import logging
from math import ceil
from typing import Optional

from yapw.methods.blocking import ack, publish

from tools import settings
from tools.services import commit, phase, set_dataset_state, set_items_state, state

logger = logging.getLogger(__name__)


def is_step_required(*steps: str) -> bool:
    return any(step in settings.STEPS for step in steps)


def process_items(client_state, channel, method, routing_key, cursors, dataset_id, ids, insert_data_items):
    ack(client_state, channel, method.delivery_tag)

    item_ids_batch = []
    items_inserted = 0

    for page_number, index in enumerate(range(0, len(ids), settings.EXTRACTOR_PAGE_SIZE)):
        insert_data_items(cursors, dataset_id, ids[index : index + settings.EXTRACTOR_PAGE_SIZE])
        commit()

        # insert_data_items() returns the id's of the rows inserted into the data_item table.
        for row in cursors["default"].fetchall():
            item_ids_batch.append(row[0])
            items_inserted += 1

            if len(item_ids_batch) >= settings.EXTRACTOR_MAX_BATCH_SIZE or items_inserted == len(ids):
                set_items_state(dataset_id, item_ids_batch, state.IN_PROGRESS)

                if items_inserted == len(ids):
                    set_dataset_state(dataset_id, state.OK, phase.CONTRACTING_PROCESS, size=items_inserted)
                else:
                    set_dataset_state(dataset_id, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=items_inserted)

                commit()

                publish(client_state, channel, {"item_ids": item_ids_batch, "dataset_id": dataset_id}, routing_key)

                item_ids_batch.clear()

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
        set_dataset_state(dataset_id, state.OK, phase)
    commit()
    if routing_key:
        publish(client_state, channel, {"dataset_id": dataset_id}, routing_key)
    ack(client_state, channel, method.delivery_tag)
