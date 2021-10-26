import tools.exchange_rates_db
from tools.currency_converter import import_data
from tools.logging_helper import init_logger


def bootstrap(logger_name):
    init_logger(logger_name)

    import_data(tools.exchange_rates_db.load())
