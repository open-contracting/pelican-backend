import logging
from typing import Any, Optional

import pika.exceptions
import psycopg2.extensions
import psycopg2.extras
import simplejson as json
from yapw import clients

from tools import settings

global db_connected
db_connected = False

logger = logging.getLogger(__name__)


class Consumer(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    pass


class Publisher(clients.Durable, clients.Blocking, clients.Base):
    pass


def encode(message: Any, content_type: Optional[str]) -> bytes:
    return json.dumps(message).encode()


def decode(body: bytes, content_type: Optional[str]) -> Any:
    return json.loads(body.decode("utf-8"))


def get_client(klass, **kwargs):
    return klass(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME, encode=encode, **kwargs)


# https://github.com/pika/pika/blob/master/examples/blocking_consume_recover_multiple_hosts.py
def consume(*args, **kwargs):
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


def publish(*args, **kwargs):
    client = get_client(Publisher)
    try:
        client.publish(*args, **kwargs)
    finally:
        client.close()


def get_cursor() -> psycopg2.extensions.cursor:
    global db_connected, db_connection
    if not db_connected:
        db_connection = psycopg2.connect(settings.DATABASE_URL)
        db_connected = True

    return db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def commit() -> None:
    db_connection.commit()


def rollback() -> None:
    db_connection.rollback()
