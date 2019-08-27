import logging

from settings.settings import get_param

global initialized
initialized = False

global logger
logger = False


def get_logger():
    if not initialized:
        print("logger not initialised")
        return False

    global logger
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
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    global initialized
    initialized = True

    return logger
