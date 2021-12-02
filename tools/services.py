from typing import Any, Optional

import psycopg2.extensions
import psycopg2.extras
import simplejson as json
from yapw import clients

from tools import settings

global db_connected
db_connected = False


class Client(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    pass


def encode(message: Any, content_type: Optional[str]) -> bytes:
    return json.dumps(message).encode()


def decode(body: bytes, content_type: Optional[str]) -> Any:
    return json.loads(body.decode("utf-8"))


def create_client():
    return Client(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME, encode=encode, decode=decode)


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
