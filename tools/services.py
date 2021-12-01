from typing import Any

import psycopg2.extras
import simplejson as json
from yapw import clients
from yapw.methods.blocking import ack, publish

from tools import settings
from tools.state import set_dataset_state

global db_connected
db_connected = False


class Client(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    pass


def encode(message: Any, content_type: str) -> bytes:
    return json.dumps(message).encode()


def decode(body: bytes, content_type: str) -> Any:
    return json.loads(body.decode("utf-8"))


def create_client():
    return Client(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME, encode=encode, decode=decode)


def get_cursor():
    global db_connected
    if not db_connected:
        global db_connection
        db_connection = psycopg2.connect(settings.DATABASE_URL)
        db_connected = True

    return db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def commit():
    db_connection.commit()


def rollback():
    db_connection.rollback()


def finish_worker(
    client_state, channel, method, dataset_id, state, phase, routing_key=None, logger_message=None, logger=None
):
    """
    Changes the dataset step status, publishes a message for the next phase and ack the received message.
    """
    set_dataset_state(dataset_id, state, phase)
    commit()
    if logger and logger_message:
        logger.info(logger_message)
    if routing_key:
        # send message for a next phase
        message = {"dataset_id": dataset_id}
        publish(client_state, channel, message, routing_key)
    ack(client_state, channel, method.delivery_tag)
