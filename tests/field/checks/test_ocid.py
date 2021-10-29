import unittest

from contracting_process.field_level.format import ocid
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = ocid
    passing = [
        "ocds-a2ef3d",
        "ocds-a2ef3dxxx",
    ]
    failing = [
        (1, "not a str"),
        ("ocds-a2ef3", "ocid prefix not in codelist"),
    ]
