from tools.logging_helper import init_logger
from tools.db import commit
from tools.db import get_cursor
from tools.db import rollback


class state():
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    OK = "OK"
    FAILED = "FAILED"


def set_dataset_state(dataset_id, state):
    cursor = get_cursor()
    cursor.execute("""
                       INSERT INTO progress_monitor_dataset (dataset_id, state, created, modified)
                       VALUES (%s, %s, now(), now());
                       """, (dataset_id, state))
    commit()


def set_item_state(dataset_id, item_id, state):
    cursor = get_cursor()
    cursor.execute("""
                       INSERT INTO progress_monitor_item (dataset_id, item_id, state, created, modified)
                       VALUES (%s, %s, %s, now(), now());
                       """, (dataset_id, item_id, state))
    commit()
