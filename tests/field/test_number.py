import unittest

from contracting_process.field_level.range import number
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = number
    passing = [
        0,
        0.0,
        1,
        1.0,
        1.1,
        "0",
        "0.0",
        "1",
        "1.0",
        "1.1",
    ]
    failing = [
        (10j, "not a real number"),
        ("invalid", "can't convert to float"),
        ("nan", "not a finite number"),
        ("inf", "not a finite number"),
        ("-inf", "not a finite number"),
        (-1, "less than 0"),
        (-1.0, "less than 0"),
        (-1.1, "less than 0"),
        ("-1", "less than 0"),
        ("-1.0", "less than 0"),
        ("-1.1", "less than 0"),
    ]
