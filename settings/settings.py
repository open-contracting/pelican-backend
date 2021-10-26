import logging
import os


class CustomLogLevels:
    MESSAGE_TRACE = 9
    CHECK_TRACE = 8
    STATE_TRACE = 7
    SUB_CHECK_TRACE = 6


# Logging

LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "WARNING"))
LOG_FILENAME = os.getenv("LOG_FILENAME")

# Batch sizes

EXTRACTOR_MAX_BATCH_SIZE = int(os.getenv("EXTRACTOR_MAX_BATCH_SIZE", 100))
KINGFISHER_PROCESS_MAX_SIZE = int(os.getenv("KINGFISHER_PROCESS_MAX_SIZE", 300000))

# Local services

# To set the search path, use, for example: postgresql:///pelican_backend?options=-csearch_path%3Dproduction,public
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql:///pelican_backend?application_name=pelican_backend")
KINGFISHER_PROCESS_DATABASE_URL = os.getenv(
    "KINGFISHER_PROCESS_DATABASE_URL", "postgresql:///kingfisher_process?application_name=kingfisher_process"
)

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://localhost")
RABBIT_EXCHANGE_NAME = os.getenv("RABBIT_EXCHANGE_NAME", "pelican_development")

# Third-party services

FIXER_IO_API_KEY = os.getenv("FIXER_IO_API_KEY")

SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_SAMPLE_RATE = os.getenv("SENTRY_SAMPLE_RATE", 1.0)

# Currency conversion

CURRENCY_CONVERTER_INTERPOLATION = os.getenv("CURRENCY_CONVERTER_INTERPOLATION", "linear")
CURRENCY_CONVERTER_EXTRAPOLATION = os.getenv("CURRENCY_CONVERTER_EXTRAPOLATION", "closest")
CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = int(
    os.getenv("CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK", 90)
)
CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = int(
    os.getenv("CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK", 180)
)

# Constants

ADDITIONAL_DOCUMENT_FORMATS = ["offline/print", "image/gif", "image/jpeg"]
