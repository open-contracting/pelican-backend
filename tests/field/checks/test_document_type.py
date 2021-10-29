import unittest

from contracting_process.field_level.codelist import document_type
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = document_type
    passing = [
        "contractGuarantees",
        "unknown",
    ]
    failing = [
        ("contractGuarantees", "not expected in planning section"),
    ]
    passing_kwargs = {"section": "tender"}
    failing_kwargs = {"section": "planning"}
    method = "calculate_section"
