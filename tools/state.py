from typing import Optional

from yapw.methods.blocking import ack, publish

from tools.services import commit, get_cursor


class state:
    IN_PROGRESS = "IN_PROGRESS"
    OK = "OK"


class phase:
    CONTRACTING_PROCESS = "CONTRACTING_PROCESS"
    DATASET = "DATASET"
    TIME_VARIANCE = "TIME_VARIANCE"
    CHECKED = "CHECKED"
    DELETED = "DELETED"


def set_dataset_state(dataset_id: int, state: str, phase: str, size: Optional[int] = None) -> None:
    """
    Upsert a dataset's progress to the given state and phase.

    :param dataset_id: the dataset's ID
    :param state: the state to set
    :param phase: the phase to be set
    :param size: number of data items to process
    """
    if size:
        sql = """
            INSERT INTO progress_monitor_dataset (dataset_id, state, phase, size)
            VALUES (%(dataset_id)s, %(state)s, %(phase)s, %(size)s)
            ON CONFLICT ON CONSTRAINT unique_dataset_id
            DO UPDATE SET state = %(state)s, phase = %(phase)s, size = %(size)s, modified = NOW()
        """
    else:
        sql = """
            INSERT INTO progress_monitor_dataset (dataset_id, state, phase, size)
            VALUES (%(dataset_id)s, %(state)s, %(phase)s, %(size)s)
            ON CONFLICT ON CONSTRAINT unique_dataset_id
            DO UPDATE SET state = %(state)s, phase = %(phase)s, modified = NOW()
        """
    with get_cursor() as cursor:
        cursor.execute(sql, {"dataset_id": dataset_id, "state": state, "phase": phase, "size": size})


def set_item_state(dataset_id: int, item_id: int, state: str) -> None:
    """
    Upsert a data item's progress to the given state.

    :param dataset_id: the dataset's ID
    :param item_id: the data item's iD
    :param state: the state to set
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
                INSERT INTO progress_monitor_item (dataset_id, item_id, state)
                VALUES (%(dataset_id)s, %(item_id)s, %(state)s)
                ON CONFLICT ON CONSTRAINT unique_dataset_id_item_id
                DO UPDATE SET state = %(state)s, modified = NOW()
            """,
            {"dataset_id": dataset_id, "item_id": item_id, "state": state},
        )


def get_processed_items_count(dataset_id: int) -> int:
    """
    Return the number of items processed.

    :param dataset_id: the dataset's ID
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) as cnt FROM progress_monitor_item WHERE dataset_id = %(id)s AND state = %(state)s",
            {"id": dataset_id, "state": state.OK},
        )
        return cursor.fetchone()["cnt"]


def get_total_items_count(dataset_id: int) -> int:
    """
    Return the number of items to process.

    :param dataset_id: the dataset's ID
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT size FROM progress_monitor_dataset WHERE dataset_id = %(id)s", {"id": dataset_id})
        return cursor.fetchone()["size"]


def get_dataset_progress(dataset_id: int) -> tuple:
    """
    Return the dataset's progress.

    :param dataset_id: the dataset's ID
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM progress_monitor_dataset WHERE dataset_id = %(id)s", {"id": dataset_id})
        return cursor.fetchone()


def finish_worker(
    client_state, channel, method, dataset_id, phase, routing_key=None, logger_message=None, logger=None
):
    """
    Changes the dataset step status, publishes a message for the next phase and ack the received message.
    """
    set_dataset_state(dataset_id, state.OK, phase)
    commit()
    if logger and logger_message:
        logger.info(logger_message)
    if routing_key:
        # send message for a next phase
        message = {"dataset_id": dataset_id}
        publish(client_state, channel, message, routing_key)
    ack(client_state, channel, method.delivery_tag)
