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
        "log_level": logging.WARNING,
        "log_filename": os.getenv("LOG_FILENAME"),
        "database_url": os.getenv("DATABASE_URL"),
        "schema": os.getenv("DATABASE_SCHEMA"),
        "exchange_name": os.getenv("RABBIT_EXCHANGE_NAME"),
        "rabbit_url": os.getenv("RABBIT_URL"),
        "extractor_max_batch_size": int(os.getenv("EXTRACTOR_MAX_BATCH_SIZE", "10")),
        "kingfisher_process_database_url": os.getenv("KINGFISHER_PROCESS_DATABASE_URL"),
        "kingfisher_process_max_size": int(os.getenv("KINGFISHER_PROCESS_MAX_SIZE", "30000")),
        "currency_converter_data_source": os.getenv("CURRENCY_CONVERTER_DATA_SOURCE", "db"),
        "currency_converter_interpolation": os.getenv("CURRENCY_CONVERTER_INTERPOLATION", "linear"),
        "currency_converter_extrapolation": os.getenv("CURRENCY_CONVERTER_EXTRAPOLATION", "closest"),
        "currency_converter_interpolation_max_days_fallback": int(
            os.getenv("CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK", "9")
        ),
        "currency_converter_extrapolation_max_days_fallback": int(
            os.getenv("CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK", "18")
        ),
        "fixer_io_api_key": os.getenv("FIXER_IO_API_KEY"),
        "fixer_io_update": os.getenv("FIXER_IO_UPDATE", "1").lower() in ("1", "true", "y", "yes"),
        "additional_document_formats": ["offline/print", "image/gif", "image/jpeg"],
        "sentry_dsn": os.getenv("SENTRY_DSN", False),
        "sentry_sample_rate": os.getenv("SENTRY_SAMPLE_RATE", 1.0),
    },
    "test": {
        "log_level": logging.DEBUG,
        "log_filename": "/tmp/dqt_test1.log",
        "database_url": "postgresql://dqt:dqt@localhost:5432/dqt",
        "schema": "development, public",
        "currency_converter_data_source": "test",
        "currency_converter_interpolation": "linear",
        "currency_converter_extrapolation": "closest",
        "currency_converter_interpolation_max_days_fallback": 90,
        "currency_converter_extrapolation_max_days_fallback": 180,
        "fixer_io_api_key": "key",
        "fixer_io_update": False,
        "additional_document_formats": ["offline/print", "image/gif", "image/jpeg"],
        "sentry_dsn": os.getenv("SENTRY_DSN", False),
        "sentry_sample_rate": os.getenv("SENTRY_SAMPLE_RATE", 1.0),
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
