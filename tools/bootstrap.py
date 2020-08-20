from tools.logging_helper import init_logger, get_logger
from settings.settings import set_environment, get_param
from tools.currency_converter import import_data
import tools.exchange_rates_db
import tools.exchange_rates_test


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
