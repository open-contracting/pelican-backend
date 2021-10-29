import unittest

from contracting_process.field_level.codelist import language
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = language
    passing = [
        "en",
    ]
    failing = [
        (1, "not in codelist"),
        ("EN", "not in codelist"),
        ("eng", "not in codelist"),
        ("en-us", "not in codelist"),
        ("en-US", "not in codelist"),
        ("en_US", "not in codelist"),
        ("xx", "not in codelist"),
    ]
