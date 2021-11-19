import functools
from urllib.parse import parse_qs, urlencode, urlsplit

import pika
from yapw import clients

from tools import settings
from tools.logging_helper import get_logger

global connected
connected = False


class Client(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    pass


def create_client():
    return Client(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME)


def publish(connection, channel, message, routing_key):
    logger.debug("Publish message from channel %s with routing_key %s", channel, routing_key)
    cb = functools.partial(publish_message, channel, message, routing_key)
    connection.add_callback_threadsafe(cb)


def connect_and_publish_message(message, routing_key):
    connection = connect()
    channel = connection.channel()
    publish_message(channel, message, routing_key)


def publish_message(channel, message, routing_key):
    routing_key = f"{settings.RABBIT_EXCHANGE_NAME}_{routing_key}"

    if not connected:
        connect()
    channel.basic_publish(
        exchange=settings.RABBIT_EXCHANGE_NAME,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    logger.log(
        settings.CustomLogLevels.MESSAGE_TRACE,
        "Published message to exchange {} with routing key {}. Message: {}".format(
            settings.RABBIT_EXCHANGE_NAME, routing_key, message
        ),
    )


def connect():
    global logger
    logger = get_logger()
    logger.debug("Connecting to RabbitMQ...")

    parsed = urlsplit(settings.RABBIT_URL)
    query = parse_qs(parsed.query)
    query.update({"blocked_connection_timeout": 1800, "heartbeat": 100})

    connection = pika.BlockingConnection(
        pika.URLParameters(parsed._replace(query=urlencode(query, doseq=True)).geturl())
    )

    global channel
    channel = connection.channel()
    channel.exchange_declare(exchange=settings.RABBIT_EXCHANGE_NAME, durable=True, exchange_type="direct")

    global connected
    connected = True
    logger.info("RabbitMQ connection established")

    return connection
