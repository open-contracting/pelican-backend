import unittest

from contracting_process.field_level.format import email
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = email
    passing = [
        "local-part@domain.com",
    ]
    failing = [
        ("local-part#domain.com", "incorrect format"),
    ]
