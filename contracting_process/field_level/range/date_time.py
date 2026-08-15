import functools
from datetime import date, datetime, timedelta, timezone

from pelican.util.checks import field_quality_check
from pelican.util.getter import parse_date

name = "date_time"
version = 2.0
lower_bound = date(1990, 1, 1)
upper_bound = date(2049, 12, 31)


def today():
    """Return the current date in UTC+14, the largest UTC offset, since ``parse_date`` discards the offset."""
    return datetime.now(tz=timezone(timedelta(hours=14))).date()


def test(value, *, past=False):  # noqa: PT028 # not a pytest test
    parsed = parse_date(value)
    if not parsed:
        return False, "can't convert to date"

    maximum = today() if past else upper_bound

    # Range tests for realism.
    return lower_bound <= parsed <= maximum, f"not in {lower_bound}/{maximum}"


calculate = field_quality_check(name, test, version)
calculate_past = functools.partial(calculate, past=True)
