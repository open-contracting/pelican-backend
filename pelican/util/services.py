import logging
from typing import Any, List, Optional, Tuple, Type, Union

import pika.exceptions
import psycopg2.extensions
import psycopg2.extras
import simplejson as json
from yapw import clients

from pelican.util import settings

global db_connected, db_connection
db_connected = False
db_connection = None

logger = logging.getLogger(__name__)


# RabbitMQ


class Consumer(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    """
    A RabbitMQ client for consuming messages.
    """


class Publisher(clients.Durable, clients.Blocking, clients.Base):
    """
    A RabbitMQ client for publishing messages.
    """


def encode(message: Any, content_type: Optional[str]) -> bytes:
    """
    Encode the body of a message for RabbitMQ.

    :param message: a decoded message
    :param content_type: the message's content type
    """
    return json.dumps(message).encode()


def decode(body: bytes, content_type: Optional[str]) -> Any:
    """
    Decode the body of a message from RabbitMQ.

    :param message: an encoded message
    :param content_type: the message's content type
    """
    return json.loads(body.decode("utf-8"))


def get_client(klass: Union[Type[Consumer], Type[Publisher]], **kwargs: Any) -> Union[Consumer, Publisher]:
    """
    Return a RabbitMQ client.

    :param klass: the class of the client to initialize
    :param kwargs: the keyword arguments to initialize the client with
    """
    return klass(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME, encode=encode, **kwargs)


# https://github.com/pika/pika/blob/master/examples/blocking_consume_recover_multiple_hosts.py
def consume(*args: Any, **kwargs: Any) -> None:
    """
    Consume messages from RabbitMQ.
    """
    while True:
        try:
            client = get_client(Consumer, prefetch_count=20, decode=decode)
            client.consume(*args, **kwargs)
            break
        # Do not recover if the connection was closed by the broker.
        except pika.exceptions.ConnectionClosedByBroker as e:  # subclass of AMQPConnectionError
            logger.warning(e)
            break
        # Recover from "Connection reset by peer".
        except pika.exceptions.StreamLostError as e:  # subclass of AMQPConnectionError
            logger.warning(e)
            continue


def publish(*args: Any, **kwargs: Any) -> None:
    """
    Publish a message to RabbitMQ.
    """
    client = get_client(Publisher)
    try:
        client.publish(*args, **kwargs)
    finally:
        client.close()


# PostgreSQL


def get_cursor() -> psycopg2.extensions.cursor:
    """
    Connect to the database, if needed, and return a database cursor.
    """
    global db_connected, db_connection
    if not db_connected:
        db_connection = psycopg2.connect(settings.DATABASE_URL)
        db_connected = True

    return db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def commit() -> None:
    """
    Commit the transaction.
    """
    db_connection.commit()


def rollback() -> None:
    """
    Rollback the transaction.
    """
    db_connection.rollback()


class state:
    IN_PROGRESS = "IN_PROGRESS"
    OK = "OK"


class phase:
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
    sql = """\
        INSERT INTO progress_monitor_dataset (dataset_id, phase, state, size)
        VALUES (%(dataset_id)s, %(phase)s, %(state)s, 0)
    """
    with get_cursor() as cursor:
        cursor.execute(sql, {"dataset_id": dataset_id, "phase": phase.CONTRACTING_PROCESS, "state": state.IN_PROGRESS})


def update_dataset_state(dataset_id: int, phase: str, state: str, size: Optional[int] = None) -> None:
    """
    Update a dataset's progress to the given phase and state.

    :param dataset_id: the dataset's ID
    :param phase: the phase to be set
    :param state: the state to set
    :param size: number of data items to process
    """
    variables = {"phase": phase, "state": state, "dataset_id": dataset_id}
    sql = """\
        UPDATE progress_monitor_dataset
        SET phase = %(phase)s, state = %(state)s, modified = now()
        WHERE dataset_id = %(dataset_id)s
    """
    if size:
        variables["size"] = size
        sql = """\
            UPDATE progress_monitor_dataset
            SET phase = %(phase)s, state = %(state)s, modified = now(), size = %(size)s
            WHERE dataset_id = %(dataset_id)s
        """
    with get_cursor() as cursor:
        cursor.execute(sql, variables)


def initialize_items_state(dataset_id: int, item_ids: List[int]) -> None:
    """
    Initialize data items' progress.

    :param dataset_id: the dataset's ID
    :param item_ids: the data items' IDs
    """
    sql = """\
        INSERT INTO progress_monitor_item (dataset_id, item_id, state)
        VALUES %s
    """
    with get_cursor() as cursor:
        psycopg2.extras.execute_values(cursor, sql, [(dataset_id, item_id, state.IN_PROGRESS) for item_id in item_ids])


def update_items_state(dataset_id: int, item_ids: List[int], state: str) -> None:
    """
    Update data items' progress to the given state.

    :param dataset_id: the dataset's ID
    :param item_ids: the data items' IDs
    :param state: the state to set
    """
    sql = """\
        UPDATE progress_monitor_item
        SET state = data.state, modified = now()
        FROM (VALUES %s) AS data (dataset_id, item_id, state)
        WHERE progress_monitor_item.dataset_id = data.dataset_id AND progress_monitor_item.item_id = data.item_id
    """
    with get_cursor() as cursor:
        psycopg2.extras.execute_values(cursor, sql, [(dataset_id, item_id, state) for item_id in item_ids])


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


def get_dataset_progress(dataset_id: int) -> Optional[Tuple[Any, ...]]:
    """
    Return the dataset's progress.

    :param dataset_id: the dataset's ID
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s", {"dataset_id": dataset_id}
        )
        return cursor.fetchone()
