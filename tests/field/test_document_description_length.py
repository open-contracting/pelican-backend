import unittest

from contracting_process.field_level.range import document_description_length
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = document_description_length
    passing = [
        ".",
        "." * 250,
    ]
    failing = [
        (1, "not a str"),  # len() would error
        ([1], "not a str"),  # len() would return
        ("." * 251, "length greater than 250", 251),
    ]
