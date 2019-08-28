from tools.logging_helper import init_logger, get_logger
from settings.settings import set_environment, get_param
from tools.converter import import_data
from tools.exchange_rates_db import load


def bootstrap(environment, logger_name):
    set_environment(environment)

    logger = init_logger(logger_name)

    # initializing converter
    if get_param('converter_data_source') == 'db':
        import_data(load())
    else:
        raise AttributeError()
