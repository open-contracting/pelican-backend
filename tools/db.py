import psycopg2.extras

from settings.settings import get_param
from tools.logging_helper import get_logger

global connected
connected = False


def get_cursor():
    global logger
    logger = get_logger()
    if not connected:
        connect()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return cursor


def get_connection():
    global logger
    logger = get_logger()
    if not connected:
        connect()
    return connection


def connect():
    logger.debug("Connecting to db...")
    global connection
    connection = psycopg2.connect(get_param("database_url"))
    logger.info("DB connection established")
    global connected
    connected = True


def commit():
    connection.commit()


def rollback():
    connection.rollback()
