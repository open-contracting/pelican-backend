from datetime import date

from pelican.util.checks import field_quality_check
from pelican.util.getter import parse_date

name = "date_time"
lower_bound = date(1990, 1, 1)
upper_bound = date(2049, 12, 31)


def test(value):
    date = parse_date(value)
    if not date:
        return False, "can't convert to date"

    # Range tests for realism.
    return lower_bound <= date <= upper_bound, f"not in {lower_bound}/{upper_bound}"


calculate = field_quality_check(name, test)
