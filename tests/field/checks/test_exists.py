import unittest

from contracting_process.field_level.coverage import exists
from tests import FieldCoverageTests


class TestCase(FieldCoverageTests, unittest.TestCase):
    module = exists
    passing = [
        {"key": None},
    ]
    failing = [
        ({}, "not set"),
        ({"other": None}, "not set"),
        ("string", "ancestor is a str, not an object", "string"),
    ]
