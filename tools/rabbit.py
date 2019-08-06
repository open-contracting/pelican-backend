import pika

from settings.settings import get_param
from tools.logging_helper import get_logger

global connected
connected = False


def publish(message, routing_key):
    if not connected:
        connect()
    channel.basic_publish(exchange=get_param("exchange_name"),
                          routing_key=routing_key,
                          body=message,
                          properties=pika.BasicProperties(delivery_mode=2))

    logger.debug("Published message to exchange {} with routing key {}".format(
        get_param("exchange_name"), routing_key))


def connect():
    global logger
    logger = get_logger()
    logger.debug("Connecting to RabbitMQ...")
    credentials = pika.PlainCredentials(get_param("rabbit_username"),
                                        get_param("rabbit_password"))

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_param("rabbit_host"),
                                                                   port=get_param(
                                                                       "rabbit_port"),
                                                                   credentials=credentials,
                                                                   blocked_connection_timeout=1800,
                                                                   heartbeat=0))
    global channel
    channel = connection.channel()

    channel.exchange_declare(exchange=get_param("exchange_name"),
                             durable='true',
                             exchange_type='direct')

    global connected
    connected = True
    logger.info("RabbitMQ connection established")


def consume(callback, routing_key):
    if not connected:
        connect()

    channel.queue_declare(queue=routing_key, durable=True)

    channel.queue_bind(exchange=get_param("exchange_name"),
                       queue=routing_key,
                       routing_key=routing_key)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=routing_key, on_message_callback=callback)

    logger.debug("Consuming messages from exchange {} with routing key {}".format(
        get_param("exchange_name"),
        routing_key))
    channel.start_consuming()
