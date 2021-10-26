import functools
import threading
from urllib.parse import parse_qs, urlencode, urlsplit

import pika

from tools import settings
from tools.logging_helper import get_logger

global connected
connected = False


def publish(connection, channel, message, routing_key):
    logger.debug("Publish message from channel {} with routing_key {}".format(channel, routing_key))
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

    connection = pika.BlockingConnection(pika.URLParameters(parsed._replace(query=urlencode(query)).geturl()))

    global channel
    channel = connection.channel()
    channel.exchange_declare(exchange=settings.RABBIT_EXCHANGE_NAME, durable=True, exchange_type="direct")

    global connected
    connected = True
    logger.info("RabbitMQ connection established")

    return connection


def consume(target_callback, routing_key):
    routing_key = f"{settings.RABBIT_EXCHANGE_NAME}_{routing_key}"

    if not connected:
        connection = connect()

        channel.queue_declare(queue=routing_key, durable=True)

        channel.queue_bind(exchange=settings.RABBIT_EXCHANGE_NAME, queue=routing_key, routing_key=routing_key)

        channel.basic_qos(prefetch_count=1)

        on_message_callback = functools.partial(on_message, args=(connection, target_callback))
        channel.basic_consume(queue=routing_key, on_message_callback=on_message_callback)

        channel.start_consuming()

    logger.debug(
        "Consuming messages from exchange {} with routing key {}".format(settings.RABBIT_EXCHANGE_NAME, routing_key)
    )


def on_message(channel, method_frame, header_frame, body, args):
    (connection, target_callback) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=target_callback, args=(connection, channel, delivery_tag, body))
    t.start()


def ack(connection, channel, delivery_tag):
    logger.debug("ACK message from channel {} with delivery tag {}".format(channel, delivery_tag))
    cb = functools.partial(ack_message, channel, delivery_tag)
    connection.add_callback_threadsafe(cb)


def ack_message(channel, delivery_tag):
    channel.basic_ack(delivery_tag)
