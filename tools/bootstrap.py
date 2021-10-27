import os

from tools.currency_converter import import_data
from tools.logging_helper import init_logger

# https://docs.pytest.org/en/latest/example/simple.html#pytest-current-test-environment-variable
if "PYTEST_CURRENT_TEST" in os.environ:
    import tools.exchange_rates_db as exchange_rates
else:
    import tools.exchange_rates_file as exchange_rates


def bootstrap(logger_name):
    init_logger(logger_name)

    import_data(exchange_rates.load())
