import unittest

from contracting_process.field_level.range import date_time
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = date_time
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
