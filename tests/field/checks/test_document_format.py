import unittest

from contracting_process.field_level.codelist import document_format
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = document_format
    passing = [
        "image/gif",
        "offline/print",
    ]
    failing = [
        (1, "not in codelist"),
        ("offline/prin", "not in codelist"),
    ]
