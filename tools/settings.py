import logging
import logging.config
import os

import sentry_sdk

# Basic configuration


class Steps:
    FIELD_COVERAGE = "field_coverage"
    FIELD_QUALITY = "field_quality"
    COMPILED_RELEASE = "compiled_release"
    DATASET = "dataset"
    TIME_BASED = "time_based"
    REPORT = "report"


class CustomLogLevels:
    CHECK_TRACE = 8


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
        },
        "loggers": {
            "pelican": {
                "handlers": ["console"],
                "level": os.getenv("LOG_LEVEL", "DEBUG"),
            },
        },
    }
)


# Project configuration

# Extractors collect this number of items before publishing a message.
EXTRACTOR_MAX_BATCH_SIZE = int(os.getenv("EXTRACTOR_MAX_BATCH_SIZE", 100))

# Do not import compiled releases whose size is larger than this number of bytes.
#
# In practice, very large releases create very large results and cause processing to fail. Since less than 0.005%
# of releases in Kingfisher Process exceed 300 kB, these releases are simply excluded instead of pursing another
# solution. (2021-10-27: n=6.12318e+07: >300 kB: 2650 0.005%; >30 kB: 195009 0.3%)
KINGFISHER_PROCESS_MAX_SIZE = int(os.getenv("KINGFISHER_PROCESS_MAX_SIZE", 300000))

# Timeout for URL availability check.
REQUESTS_TIMEOUT = 30

# Do not set in development, to skip updates to exchange rates, and to save quota.
FIXER_IO_API_KEY = os.getenv("FIXER_IO_API_KEY")

# The following settings configure how the rate is determined if a date is missing a rate.

# Interpolation refers to the behavior when the date is between dates with known rates. If disabled, the value is not
# converted. Otherwise, the rate is determined by either using linear interpolation ("linear") or copying the rate of
# the closest date ("closest").
CURRENCY_CONVERTER_INTERPOLATION = os.getenv("CURRENCY_CONVERTER_INTERPOLATION", "linear")
# If the distance to the nearby date(s) is greater than this number of days, the value is not converted. Set to -1 to
# set the limit to infinity.
CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = int(
    os.getenv("CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK", 90)
)

# Extrapolation refers to the behavior when the date is outside dates with known rates. if disabled, the value is not
# converted. Otherwise, the reate is determined by copying the rate of the closest date ("closest").
CURRENCY_CONVERTER_EXTRAPOLATION = os.getenv("CURRENCY_CONVERTER_EXTRAPOLATION", "closest")
# If the distance to the closest date is greater than this number of days, the value is not converted. Set to -1 to
# set the limit to infinity.
CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = int(
    os.getenv("CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK", 180)
)

# A comma-separated list of steps to run. Default to all.
STEPS = os.getenv(
    "PELICAN_BACKEND_STEPS",
    ",".join(getattr(Steps, attr) for attr in dir(Steps) if not attr.startswith("__")),
).split(",")

# Dependency configuration

# To set the search path, use, for example: postgresql:///pelican_backend?options=-csearch_path%3Dproduction,public
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql:///pelican_backend?application_name=pelican_backend")
KINGFISHER_PROCESS_DATABASE_URL = os.getenv(
    "KINGFISHER_PROCESS_DATABASE_URL", "postgresql:///kingfisher_process?application_name=pelican_backend"
)

# The connection string for RabbitMQ.
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://localhost")
# The name of the RabbitMQ exchange. Follow the pattern `{project}_{service}_{environment}`.
RABBIT_EXCHANGE_NAME = os.getenv("RABBIT_EXCHANGE_NAME", "pelican_development")

if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=0,  # The Sentry plan does not include Performance.
    )
