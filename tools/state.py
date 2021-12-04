from typing import Any, List, Optional, Tuple

from psycopg2.extras import execute_values

from tools.services import get_cursor


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
        sql = """\
            INSERT INTO progress_monitor_dataset (dataset_id, state, phase, size)
            VALUES (%(dataset_id)s, %(state)s, %(phase)s, %(size)s)
            ON CONFLICT (dataset_id)
            DO UPDATE SET state = %(state)s, phase = %(phase)s, size = %(size)s, modified = now()
        """
    else:
        sql = """\
            INSERT INTO progress_monitor_dataset (dataset_id, state, phase, size)
            VALUES (%(dataset_id)s, %(state)s, %(phase)s, %(size)s)
            ON CONFLICT (dataset_id)
            DO UPDATE SET state = %(state)s, phase = %(phase)s, modified = now()
        """
    with get_cursor() as cursor:
        cursor.execute(sql, {"dataset_id": dataset_id, "state": state, "phase": phase, "size": size})


def set_items_state(dataset_id: int, item_ids: List[int], state: str) -> None:
    """
    Upsert data items' progress to the given state.

    :param dataset_id: the dataset's ID
    :param item_ids: the data items' IDs
    :param state: the state to set
    """
    with get_cursor() as cursor:
        sql = """\
            INSERT INTO progress_monitor_item (dataset_id, item_id, state)
            VALUES %s
            ON CONFLICT (dataset_id, item_id)
            DO UPDATE SET state = excluded.state, modified = now()
        """
        execute_values(cursor, sql, [(dataset_id, item_id, state) for item_id in item_ids])


def get_processed_items_count(dataset_id: int) -> int:
    """
    Return the number of items processed.

    :param dataset_id: the dataset's ID
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) cnt FROM progress_monitor_item WHERE dataset_id = %(dataset_id)s AND state = %(state)s",
            {"dataset_id": dataset_id, "state": state.OK},
        )
        return cursor.fetchone()["cnt"]


def get_total_items_count(dataset_id: int) -> int:
    """
    Return the number of items to process.

    :param dataset_id: the dataset's ID
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT size FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s", {"dataset_id": dataset_id}
        )
        return cursor.fetchone()["size"]


def get_dataset_progress(dataset_id: int) -> Tuple[Any, ...]:
    """
    Return the dataset's progress.

    :param dataset_id: the dataset's ID
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s", {"dataset_id": dataset_id}
        )
        return cursor.fetchone()
