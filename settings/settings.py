import logging
import os


# custom log levels
class CustomLogLevels:
    MESSAGE_TRACE = 9
    CHECK_TRACE = 8
    STATE_TRACE = 7
    SUB_CHECK_TRACE = 6


environment = None

config_data = {
    "docker": {
        "log_level": logging.DEBUG,
        "log_filename": os.getenv("LOG_FILENAME"),
        "host": os.getenv("HOST"),
        "user": os.getenv("USER"),
        "password": os.getenv("PASSWORD"),
        "port": os.getenv("PORT"),
        "db": os.getenv("DB"),
        "schema": os.getenv("SCHEMA"),
        "exchange_name": os.getenv("EXCHANGE_NAME"),
        "rabbit_host": os.getenv("RABBIT_HOST"),
        "rabbit_port": os.getenv("RABBIT_PORT"),
        "rabbit_username": os.getenv("RABBIT_USERNAME"),
        "rabbit_password": os.getenv("RABBIT_PASSWORD"),
        "extractor_max_batch_size": os.getenv("EXTRACTOR_MAX_BATCH_SIZE"),
        "kf_extractor_host": os.getenv("KF_EXTRACTOR_HOST"),
        "kf_extractor_user": os.getenv("KF_EXTRACTOR_USER"),
        "kf_extractor_password": os.getenv("KF_EXTRACTOR_PASSWORD"),
        "kf_extractor_port": os.getenv("KF_EXTRACTOR_PORT"),
        "kf_extractor_db": os.getenv("KF_EXTRACTOR_DB"),
        "kf_extractor_max_size": os.getenv("KF_EXTRACTOR_MAX_SIZE"),
        "currency_converter_data_source": os.getenv("CURRENCY_CONVERTER_DATA_SOURCE"),
        "currency_converter_interpolation": os.getenv("CURRENCY_CONVERTER_INTERPOLATION"),
        "currency_converter_extrapolation": os.getenv("CURRENCY_CONVERTER_EXTRAPOLATION"),
        "currency_converter_interpolation_max_days_fallback": os.getenv(
            "CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK"
        ),
        "currency_converter_extrapolation_max_days_fallback": os.getenv(
            "CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK"
        ),
        "fixer_io_api_key": os.getenv("FIXER_IO_API_KEY"),
        "fixer_io_update": os.getenv("FIXER_IO_UPDATE", "1").lower() in ("1", "true", "y", "yes"),
        "additional_document_formats": ["offline/print", "image/gif", "image/jpeg"],
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
        "fixer_io_api_key": "key",
        "fixer_io_update": False,
        "additional_document_formats": ["offline/print", "image/gif", "image/jpeg"],
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
