import unittest
from datetime import timedelta

from contracting_process.field_level.range import date_time
from tests import FieldQualityTests

today = date_time.today()


class TestCase(FieldQualityTests, unittest.TestCase):
    module = date_time
    version = 2.0
    passing = [
        "1990-1-1",
        "2049-12-31",
        "1997-08-09",
    ]
    failing = [
        (20000101, "can't convert to date"),
        ("invalid", "can't convert to date"),
        ("2000-02-30", "can't convert to date"),
        ("1969-12-31", "not in 1990-01-01/2049-12-31"),
        ("2050-01-01", "not in 1990-01-01/2049-12-31"),
    ]


class PastTestCase(FieldQualityTests, unittest.TestCase):
    module = date_time
    method = "calculate_past"
    version = 2.0
    passing = [
        "1990-1-1",
        today.isoformat(),
        "1997-08-09",
    ]
    failing = [
        (20000101, "can't convert to date"),
        ("invalid", "can't convert to date"),
        ("2000-02-30", "can't convert to date"),
        ("1969-12-31", f"not in 1990-01-01/{today}"),
        ("2049-12-31", f"not in 1990-01-01/{today}"),
        ((today + timedelta(days=1)).isoformat(), f"not in 1990-01-01/{today}"),
    ]
