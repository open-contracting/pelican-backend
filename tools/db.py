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
    return cursor


def connect():
    logger.debug("Connecting to db...")
    global connection
    connection = psycopg2.connect(
        "host='{}' dbname='{}' user='{}' password='{}' port ='{}'".format(
            get_param("host"), get_param("db"), get_param("user"), get_param("password"), get_param("port")))

    global cursor
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    logger.info("DB connection established")
    set_schema(get_param("schema"))

    global connected
    connected = True
    return cursor


def set_schema(schema):
    logger.debug("Setting schema to {}".format(schema))
    cursor.execute("SET search_path to {};".format(schema))


def commit():
    connection.commit()


def rollback():
    connection.rollback()
