import functools
import threading

import pika

from settings.settings import CustomLogLevels, get_param
from tools.logging_helper import get_logger

global connected
connected = False


def publish(connection, channel, message, routing_key):
    logger.debug(
        "Publish message from channel {} with routing_key {}".format(channel, routing_key)
    )
    cb = functools.partial(publish_message, channel, message, routing_key)
    connection.add_callback_threadsafe(cb)


def publish_message(channel, message, routing_key):
    if not connected:
        connect()
    channel.basic_publish(
        exchange=get_param("exchange_name"),
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    logger.log(
        CustomLogLevels.MESSAGE_TRACE,
        "Published message to exchange {} with routing key {}. Message: {}".format(
            get_param("exchange_name"), routing_key, message
        ),
    )


def connect():
    global logger
    logger = get_logger()
    logger.debug("Connecting to RabbitMQ...")
    credentials = pika.PlainCredentials(get_param("rabbit_username"), get_param("rabbit_password"))

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=get_param("rabbit_host"),
            port=get_param("rabbit_port"),
            credentials=credentials,
            blocked_connection_timeout=1800,
            heartbeat=100,
        )
    )

    global channel
    channel = connection.channel()

    channel.exchange_declare(exchange=get_param("exchange_name"), durable="true", exchange_type="direct")

    global connected
    connected = True
    logger.info("RabbitMQ connection established")

    return connection


def consume(target_callback, routing_key):
    if not connected:
        connection = connect()

        channel.queue_declare(queue=routing_key, durable=True)

        channel.queue_bind(exchange=get_param("exchange_name"), queue=routing_key, routing_key=routing_key)

        channel.basic_qos(prefetch_count=1)

        on_message_callback = functools.partial(on_message, args=(connection, target_callback))
        channel.basic_consume(queue=routing_key, on_message_callback=on_message_callback)

        channel.start_consuming()

    logger.debug(
        "Consuming messages from exchange {} with routing key {}".format(get_param("exchange_name"), routing_key)
    )


def on_message(channel, method_frame, header_frame, body, args):
    (connection, target_callback) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=target_callback, args=(connection, channel, delivery_tag, body))
    t.start()


def ack(connection, channel, delivery_tag):
    logger.debug(
        "ACK message from channel {} with delivery tag {}".format(channel, delivery_tag)
    )
    cb = functools.partial(ack_message, channel, delivery_tag)
    connection.add_callback_threadsafe(cb)


def ack_message(channel, delivery_tag):
    channel.basic_ack(delivery_tag)
