import unittest

from contracting_process.field_level.coverage import non_empty
from tests import FieldCoverageTests


class TestCase(FieldCoverageTests, unittest.TestCase):
    module = non_empty
    passing = [
        {"key": {"key": None}},
        {"key": [None]},
        {"key": "value"},
        {"key": 0},
        {"key": True},
        {"key": False},
    ]
    failing = [
        ({}, "not set"),
        ({"other": None}, "not set"),
        ("string", "parent is a str, not an object", "string"),
        ({"key": {}}, "empty object", {}),
        ({"key": []}, "empty array", []),
        ({"key": ""}, "empty string", ""),
        ({"key": None}, "null value"),
    ]
