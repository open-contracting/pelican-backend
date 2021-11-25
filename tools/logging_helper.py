import logging

from tools import settings

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

    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    global initialized
    initialized = True

    return logger
