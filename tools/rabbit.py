import functools

import pika
from yapw import clients

from tools import settings
from tools.logging_helper import get_logger

logger = get_logger()


class Client(clients.Threaded, clients.Durable, clients.Blocking, clients.Base):
    pass


def create_client():
    return Client(url=settings.RABBIT_URL, exchange=settings.RABBIT_EXCHANGE_NAME)


def publish(connection, channel, message, routing_key):
    logger.debug("Publish message from channel %s with routing_key %s", channel, routing_key)
    cb = functools.partial(publish_message, channel, message, routing_key)
    connection.add_callback_threadsafe(cb)


def publish_message(channel, message, routing_key):
    routing_key = f"{settings.RABBIT_EXCHANGE_NAME}_{routing_key}"

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
