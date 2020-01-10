import logging


# custom log levels
class CustomLogLevels:
    MESSAGE_TRACE = 9
    CHECK_TRACE = 8
    STATE_TRACE = 7
    SUB_CHECK_TRACE = 6

environment = None

config_data = {
    "development": {
        "log_level": logging.DEBUG,
        "log_filename": "/tmp/dqt.log",
        "host": "localhost",
        "user": "dqt",
        "password": "dqt",
        "port": "5432",
        "db": "dqt",
        "schema": "development, postgis, public",
        "exchange_name": "dqt_development",
        "rabbit_host": "localhost",
        "rabbit_port": "5672",
        "rabbit_username": "rabbit",
        "rabbit_password": "rabbit",
        "extractor_max_batch_size": 100,
        "kf_extractor_host": "scrape.kingfisher.open-contracting.org",
        "kf_extractor_user": "ocdskfpreadonly",
        "kf_extractor_password": "LJNBQvRT83QTi9og",
        "kf_extractor_port": "5432",
        "kf_extractor_db": "ocdskingfisherprocess",
        "currency_converter_data_source": "db",
        "currency_converter_interpolation": "linear",
        "currency_converter_extrapolation": "closest",
        "currency_converter_interpolation_max_days_fallback": 90,
        "currency_converter_extrapolation_max_days_fallback": 180,
        "fixer_io_api_key": "c744ed8d097ea8f6d4daeb2fc56a0e44",
        "fixer_io_update": False,
    },
    "production": {
        "log_level": logging.DEBUG,
        "log_filename": "/tmp/dqt.log",
        "host": "localhost",
        "user": "dqt",
        "password": "dqt",
        "port": "5432",
        "db": "dqt",
        "schema": "production, postgis, public",
        "exchange_name": "dqt_production",
        "rabbit_host": "localhost",
        "rabbit_port": "5672",
        "rabbit_username": "rabbit",
        "rabbit_password": "rabbit",
        "extractor_max_batch_size": 100,
        "kf_extractor_host": "scrape.kingfisher.open-contracting.org",
        "kf_extractor_user": "ocdskfpreadonly",
        "kf_extractor_password": "LJNBQvRT83QTi9og",
        "kf_extractor_port": "5432",
        "kf_extractor_db": "ocdskingfisherprocess",
        "currency_converter_data_source": "db",
        "currency_converter_interpolation": "linear",
        "currency_converter_extrapolation": "closest",
        "currency_converter_interpolation_max_days_fallback": 90,
        "currency_converter_extrapolation_max_days_fallback": 180,
        "fixer_io_api_key": "c744ed8d097ea8f6d4daeb2fc56a0e44",
        "fixer_io_update": False,
    },
    "test": {
        "log_level": logging.DEBUG,
        "log_filename": "/tmp/dqt_test1.log",
        "host": "localhost",
        "user": "dqt",
        "password": "dqt",
        "port": "5432",
        "db": "dqt",
        "schema": "development, postgis, public",
        "currency_converter_data_source": "test",
        "currency_converter_interpolation": "linear",
        "currency_converter_extrapolation": "closest",
        "currency_converter_interpolation_max_days_fallback": 90,
        "currency_converter_extrapolation_max_days_fallback": 180,
        "fixer_io_api_key": "c744ed8d097ea8f6d4daeb2fc56a0e44",
        "fixer_io_update": False,
    },
    "kuba_development": {
        "log_level": logging.DEBUG,
        "log_filename": "/tmp/dqt.log",
        "host": "localhost",
        "user": "dqt",
        "password": "dqt",
        "port": "22002",
        "db": "dqt",
        "schema": "development, postgis, public",
        "exchange_name": "dqt_development",
        "rabbit_host": "localhost",
        "rabbit_port": "22000",
        "rabbit_username": "rabbit",
        "rabbit_password": "rabbit",
        "extractor_max_batch_size": 100,
        "kf_extractor_host": "scrape.kingfisher.open-contracting.org",
        "kf_extractor_user": "ocdskfpreadonly",
        "kf_extractor_password": "LJNBQvRT83QTi9og",
        "kf_extractor_port": "5432",
        "kf_extractor_db": "ocdskingfisherprocess",
        "currency_converter_data_source": "db",
        "currency_converter_interpolation": "linear",
        "currency_converter_extrapolation": "closest",
        "currency_converter_interpolation_max_days_fallback": 90,
        "currency_converter_extrapolation_max_days_fallback": 180,
        "fixer_io_api_key": "c744ed8d097ea8f6d4daeb2fc56a0e44",
        "fixer_io_update": False,
    },
    "mirek_development": {
        "log_level": logging.DEBUG,
        "log_filename": "/tmp/mirek_dqt.log",
        "host": "localhost",
        "user": "dqt",
        "password": "dqt",
        "port": "25001",
        "db": "dqt",
        "schema": "development, postgis, public",
        "exchange_name": "dqt_development",
        "rabbit_host": "localhost",
        "rabbit_port": "25002",
        "rabbit_username": "rabbit",
        "rabbit_password": "rabbit",
        "extractor_max_batch_size": 100,
        "kf_extractor_host": "scrape.kingfisher.open-contracting.org",
        "kf_extractor_user": "ocdskfpreadonly",
        "kf_extractor_password": "LJNBQvRT83QTi9og",
        "kf_extractor_port": "5432",
        "kf_extractor_db": "ocdskingfisherprocess",
        "currency_converter_data_source": "db",
        "currency_converter_interpolation": "linear",
        "currency_converter_extrapolation": "closest",
        "currency_converter_interpolation_max_days_fallback": 90,
        "currency_converter_extrapolation_max_days_fallback": 180,
        "fixer_io_api_key": "c744ed8d097ea8f6d4daeb2fc56a0e44",
        "fixer_io_update": False,
    },
}


def get_param(param_name):
    global environment
    return config_data[environment][param_name]


def set_environment(environment_name):
    global environment
    environment = environment_name


def get_environment():
    global environment
    return environment
