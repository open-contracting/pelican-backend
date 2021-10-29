import unittest

from contracting_process.field_level.codelist import identifier_scheme
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = identifier_scheme
    passing = [
        "XI-LEI",
    ]
    failing = [
        (1, "not in codelist"),
        ("XI-LE", "not in codelist"),
    ]
