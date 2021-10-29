import unittest

from contracting_process.field_level.format import telephone
from tests import FieldQualityTests


class TestCase(FieldQualityTests, unittest.TestCase):
    module = telephone
    passing = [
        "+420123456789",
        # Grouping
        "+4 20123456789",
        # Punctuation
        "+420 123 456 789",
        "+420-123-456-789",
        "+420.123.456.789",
        "+420/123/456/789",
        # Extension
        "+420123456789x",
        "+420123456789x1",
        "+420123456789x1234567",
    ]
    failing = [
        (1, "not a str"),
        ("invalid", "incorrect format: (1) The string supplied did not seem to be a phone number."),
        ("+420_123_456_789", "incorrect format: (1) The string supplied did not seem to be a phone number."),
        # + sign
        ("420 123456789", "incorrect format: (0) Missing or invalid default region."),
        ("00 420 123456789", "incorrect format: (0) Missing or invalid default region."),
        # County code
        ("123456789", "incorrect format: (0) Missing or invalid default region."),
        ("+999123456789", "incorrect format: (0) Could not interpret numbers after plus-sign."),
        # Local number
        ("+42012345678", "incorrect format"),
        ("+4201234567891234", "incorrect format"),
        # Extension
        ("+420123456789x12345678", "incorrect format"),
    ]
