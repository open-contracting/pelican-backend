from tools.logging_helper import init_logger, get_logger
from settings.settings import set_environment


def bootstrap(environment, logger_name):
    set_environment(environment)

    logger = init_logger(logger_name)
