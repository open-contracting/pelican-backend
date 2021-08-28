import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from settings.settings import get_param

global initialized
initialized = False

global logger
logger = None


def get_logger():
    if not initialized:
        init_logger("system")

    return logger


def init_logger(logger_name):
    if not logger_name:
        logger_name = "generic"

    global logger
    logger = logging.getLogger(logger_name)

    logger.setLevel(get_param("log_level"))

    # create file handler which logs even debug messages
    fh = logging.FileHandler(get_param("log_filename"))
    fh.setLevel(get_param("log_level"))
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(get_param("log_level"))
    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    if get_param("sentry_dsn"):
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        sentry_sdk.init(
            dsn=get_param("sentry_dsn"),
            integrations=[sentry_logging],
        )

    global initialized
    initialized = True

    return logger
