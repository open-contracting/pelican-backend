import logging

import psycopg2.extras

from tools import settings

logger = logging.getLogger("pelican.tools.db")

global connected
connected = False


def get_cursor():
    if not connected:
        connect()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return cursor


def get_connection():
    if not connected:
        connect()
    return connection


def connect():
    logger.debug("Connecting to db...")
    global connection
    connection = psycopg2.connect(settings.DATABASE_URL)
    logger.info("DB connection established")
    global connected
    connected = True


def commit():
    connection.commit()


def rollback():
    connection.rollback()
