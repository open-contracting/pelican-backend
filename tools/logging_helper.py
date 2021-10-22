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
        init_logger("pelican_backend")

    return logger


def init_logger(logger_name):
    if not logger_name:
        logger_name = "generic"

    global logger
    logger = logging.getLogger(logger_name)

    logger.setLevel(get_param("log_level"))

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(message)s")

    log_filename = get_param("log_filename")
    if log_filename:
        # create file handler which logs even debug messages
        fh = logging.FileHandler(log_filename)
        fh.setLevel(get_param("log_level"))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(get_param("log_level"))
    ch.setFormatter(formatter)
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
