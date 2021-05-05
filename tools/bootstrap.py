import tools.exchange_rates_db
import tools.exchange_rates_test
from settings.settings import get_param, set_environment
from tools.currency_converter import import_data
from tools.logging_helper import get_logger, init_logger


def bootstrap(environment, logger_name):
    set_environment(environment)

    logger = init_logger(logger_name)

    # initializing converter
    if get_param('currency_converter_data_source') == 'db':
        import_data(tools.exchange_rates_db.load())
    elif get_param('currency_converter_data_source') == 'test':
        import_data(tools.exchange_rates_test.load())
    else:
        raise AttributeError()
