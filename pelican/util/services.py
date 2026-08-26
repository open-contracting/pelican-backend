import logging
import threading
from collections.abc import Iterable
from functools import cache
from typing import Any

import orjson
import psycopg
from psycopg import sql
from psycopg.abc import Params, QueryNoTemplate
from psycopg.rows import dict_row
from psycopg.types.json import set_json_dumps, set_json_loads
from yapw.clients import AsyncConsumer, Blocking

from pelican.util import settings

# Open one connection per thread, so that one thread doesn't commit another's incomplete work.
db = threading.local()

logger = logging.getLogger(__name__)


# RabbitMQ


def encode(message: Any, content_type: str | None) -> bytes:
    """
    Encode the body of a message for RabbitMQ.

    :param message: a decoded message
    :param content_type: the message's content type
    """
    return orjson.dumps(message)


def decode(body: bytes, content_type: str | None) -> Any:
    """
    Decode the body of a message from RabbitMQ.

    :param message: an encoded message
    :param content_type: the message's content type
    """
    return orjson.loads(body)


YAPW_KWARGS = {
    "url": settings.RABBIT_URL,
    "exchange": settings.RABBIT_EXCHANGE_NAME,
    "encode": encode,
    "decode": decode,
}

# Increase the consumer timeout from RabbitMQ's 30-minute default, for workers with long-running callbacks.
# https://www.rabbitmq.com/consumers.html
CONSUMER_TIMEOUT_ARGUMENTS = {"x-consumer-timeout": 3 * 60 * 60 * 1000}  # 3 hours, in milliseconds


def consume(*args: Any, prefetch_count=1, **kwargs: Any) -> None:
    """Consume messages from RabbitMQ."""
    client = AsyncConsumer(*args, prefetch_count=prefetch_count, **kwargs, **YAPW_KWARGS)
    client.start()


def publish(*args: Any, **kwargs: Any) -> None:
    """Publish a message to RabbitMQ."""
    client = Blocking(**YAPW_KWARGS)
    try:
        client.publish(*args, **kwargs)
    finally:
        client.close()


# PostgreSQL

set_json_dumps(orjson.dumps)
set_json_loads(orjson.loads)


def get_connection() -> psycopg.Connection[dict[str, Any]]:
    """Connect to the database, if needed, and return the database connection."""
    if not hasattr(db, "connection"):
        db.connection = psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)

    return db.connection


def get_cursor(name="") -> psycopg.Cursor[dict[str, Any]]:
    """Return a database cursor. If a name is provided, the cursor is server-side."""
    connection = get_connection()

    if name:
        # https://github.com/django/django/blob/stable/4.2.x/django/db/backends/postgresql/base.py#L469
        db.cursor_idx = getattr(db, "cursor_idx", 0) + 1
        cursor_name = f"{name}-{threading.current_thread().ident}-{db.cursor_idx}"
        # Avoid "named cursor isn't valid anymore". Another option is to use a separate connection.
        # https://www.psycopg.org/psycopg3/docs/advanced/cursors.html#server-side-cursors
        return connection.cursor(name=cursor_name, withhold=True)

    return connection.cursor()


def execute(statement: QueryNoTemplate, variables: Params | None = None) -> psycopg.Cursor[dict[str, Any]]:
    """Execute a statement, and return a cursor, from which to read any results."""
    return get_connection().execute(statement, variables)


def executemany(statement: QueryNoTemplate, variables_seq: Iterable[Params]) -> None:
    """Execute a statement, once for each set of parameters."""
    with get_connection().cursor() as cursor:
        cursor.executemany(statement, variables_seq)


def commit() -> None:
    """Commit the transaction."""
    get_connection().commit()


def rollback() -> None:
    """Rollback the transaction."""
    get_connection().rollback()


class State:
    IN_PROGRESS = "IN_PROGRESS"
    OK = "OK"


class Phase:
    CONTRACTING_PROCESS = "CONTRACTING_PROCESS"
    DATASET = "DATASET"
    TIME_VARIANCE = "TIME_VARIANCE"
    CHECKED = "CHECKED"
    DELETED = "DELETED"


def initialize_dataset_state(dataset_id: int) -> None:
    """
    Initialize a dataset's progress.

    :param dataset_id: the dataset's ID
    """
    execute(
        """\
        INSERT INTO progress_monitor_dataset (dataset_id, phase, state, size)
        VALUES (%(dataset_id)s, %(phase)s, %(state)s, 0)
        """,
        {"dataset_id": dataset_id, "phase": Phase.CONTRACTING_PROCESS, "state": State.IN_PROGRESS},
    )


def update_dataset_state(dataset_id: int, phase: str, state: str, size: int | None = None) -> None:
    """
    Update a dataset's progress to the given phase and state.

    :param dataset_id: the dataset's ID
    :param phase: the phase to be set
    :param state: the state to set
    :param size: number of data items to process
    """
    variables = {"phase": phase, "state": state, "dataset_id": dataset_id}
    statement = """\
        UPDATE progress_monitor_dataset
        SET phase = %(phase)s, state = %(state)s, modified = now()
        WHERE dataset_id = %(dataset_id)s
    """
    if size:
        variables["size"] = size
        statement = """\
            UPDATE progress_monitor_dataset
            SET phase = %(phase)s, state = %(state)s, modified = now(), size = %(size)s
            WHERE dataset_id = %(dataset_id)s
        """
    execute(statement, variables)


def claim_dataset_phase(dataset_id: int, from_phase: str, from_state: str, phase: str, state: str) -> bool:
    """
    Update and commit a dataset's progress to the given phase and state, if it is in the given phase and state.

    Use this instead of :func:`update_dataset_state`, if messages for the same dataset can be processed concurrently.

    :param dataset_id: the dataset's ID
    :param from_phase: the phase the dataset must be in
    :param from_state: the state the dataset must be in
    :param phase: the phase to set
    :param state: the state to set
    :return: whether the dataset was claimed
    """
    # If another connection claimed the dataset but hasn't committed, this blocks until it commits, then matches 0
    # rows, since the WHERE condition is re-evaluated in the READ COMMITTED isolation level.
    cursor = execute(
        """\
        UPDATE progress_monitor_dataset
        SET phase = %(phase)s, state = %(state)s, modified = now()
        WHERE dataset_id = %(dataset_id)s AND phase = %(from_phase)s AND state = %(from_state)s
        """,
        {"dataset_id": dataset_id, "from_phase": from_phase, "from_state": from_state, "phase": phase, "state": state},
    )
    commit()
    return cursor.rowcount == 1


def initialize_items_state(dataset_id: int, item_ids: list[int]) -> None:
    """
    Initialize data items' progress.

    :param dataset_id: the dataset's ID
    :param item_ids: the data items' IDs
    """
    executemany(
        """\
        INSERT INTO progress_monitor_item (dataset_id, item_id, state)
        VALUES (%(dataset_id)s, %(item_id)s, %(state)s)
        """,
        [{"dataset_id": dataset_id, "item_id": item_id, "state": State.IN_PROGRESS} for item_id in item_ids],
    )


def update_items_state(dataset_id: int, item_ids: list[int], state: str) -> None:
    """
    Update data items' progress to the given state.

    :param dataset_id: the dataset's ID
    :param item_ids: the data items' IDs
    :param state: the state to set
    """
    item_ids = list(item_ids)
    if not item_ids:
        return

    records = sql.SQL(", ").join(sql.SQL("(%s, %s, %s)") for _ in item_ids)
    statement = sql.SQL(
        """\
        UPDATE progress_monitor_item
        SET state = data.state, modified = now()
        FROM (VALUES {}) AS data (dataset_id, item_id, state)
        WHERE progress_monitor_item.dataset_id = data.dataset_id AND progress_monitor_item.item_id = data.item_id
        """
    ).format(records)
    execute(statement, [parameter for item_id in item_ids for parameter in (dataset_id, item_id, state)])


def get_processed_items_count(dataset_id: int) -> int:
    """
    Return the number of items processed.

    :param dataset_id: the dataset's ID
    """
    return execute(
        "SELECT COUNT(*) cnt FROM progress_monitor_item WHERE dataset_id = %(dataset_id)s AND state = %(state)s",
        {"dataset_id": dataset_id, "state": State.OK},
    ).fetchone()["cnt"]


# The check.dataset worker calls this function when phase=CONTRACTING_PROCESS and state=OK, at which point size is set.
@cache
def get_total_items_count(dataset_id: int) -> int:
    """
    Return the number of items to process.

    :param dataset_id: the dataset's ID
    """
    return execute(
        "SELECT size FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s", {"dataset_id": dataset_id}
    ).fetchone()["size"]


def get_dataset_progress(dataset_id: int) -> dict[str, Any] | None:
    """
    Return the dataset's progress.

    :param dataset_id: the dataset's ID
    """
    return execute(
        "SELECT * FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s", {"dataset_id": dataset_id}
    ).fetchone()
