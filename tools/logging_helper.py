import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from settings import settings

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

    logger.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(message)s")

    log_filename = settings.LOG_FILENAME
    if log_filename:
        # create file handler which logs even debug messages
        fh = logging.FileHandler(log_filename)
        fh.setLevel(settings.LOG_LEVEL)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if settings.SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[sentry_logging],
        )

    global initialized
    initialized = True

    return logger
