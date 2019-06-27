from tools.db import commit, get_cursor, rollback
from tools.logging_helper import init_logger


class state():
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    OK = "OK"
    FAILED = "FAILED"


class phase():
    PLANNED = "PLANNED"
    CONTRACTING_PROCESS = "CONTRACTING_PROCESS"
    DATASET = "DATASET"
    TIME_VARIANCE = "TIME_VARIANCE"
    CHECKED = "CHECKED"


def set_dataset_state(dataset_id, state, phase, size=None):
    """Upserts dataset to provided state and phase.

    Args:
        dataset_id: id of dataset to be updated
        state: state to be set
        phase: phase to be set
        size: amount of contract process items to be processed
    """
    cursor = get_cursor()
    cursor.execute("""
                       INSERT INTO progress_monitor_dataset
                       (dataset_id, state, phase, size, created, modified)
                       VALUES
                       (%s, %s, %s, %s, now(), now())
                       ON CONFLICT ON CONSTRAINT unique_dataset_id
                       DO UPDATE SET state = %s, phase = %s, modified = now();
                       """, (dataset_id, state, phase, size, state, phase))


def set_item_state(dataset_id, item_id, state):
    """Upserts dataset item to provided state.

    Args:
        dataset_id: id of dataset to be updated
        item_id: id of item to be updated
        state: state to be set
    """
    cursor = get_cursor()
    cursor.execute("""
                       INSERT INTO progress_monitor_item
                       (dataset_id, item_id, state, created, modified)
                       VALUES
                       (%s, %s, %s, now(), now())
                       ON CONFLICT ON CONSTRAINT unique_dataset_id_item_id
                       DO UPDATE SET state = %s, modified = now();
                       """, (dataset_id, item_id, state, state))


def get_processed_items_count(dataset_id):
    """Checks how many items were processed already.

    Args:
        dataset_id: id of dataset to be checked
    Returns:
        get number of processed items
    """
    cursor = get_cursor()
    cursor.execute("""
                       SELECT count(*) as cnt FROM progress_monitor_item
                       WHERE
                       dataset_id = %s
                       AND state IN (%s, %s);
                       """, (dataset_id, state.OK, state.FAILED))

    result = cursor.fetchone()

    return result['cnt']


def get_total_items_count(dataset_id):
    """Checks how many items were processed already.

    Args:
        dataset_id: id of dataset to be checked
    Returns:
        get number of processed items
    """
    cursor = get_cursor()
    cursor.execute("""
                       SELECT size as size FROM progress_monitor_dataset
                       WHERE
                       dataset_id = %s;
                    """, (dataset_id,))

    result = cursor.fetchone()

    return result['size']


def get_dataset(dataset_id):
    """Returns dataset identified by its id

    Args:
        dataset_id: id of dataset to be retrieved
    Returns:
        dataset
    """
    cursor = get_cursor()
    cursor.execute("""
                       SELECT * FROM progress_monitor_dataset
                       WHERE
                       dataset_id = %s;
                    """, (dataset_id,))

    result = cursor.fetchone()

    return result
