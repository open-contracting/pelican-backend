import unittest

from contracting_process.resource_level.coherent import tender_status
from tests import CompiledReleaseTests


class TestCase(CompiledReleaseTests, unittest.TestCase):
    module = tender_status
    skipping = [
        (
            {"tender": {}},
            "criteria not met",
        ),
        (
            {"tender": {"status": "invalid"}},  # invalid
            "criteria not met",
        ),
    ]
    passing = [
        ({"tender": {"status": "planning"}}, None, 1),
        ({"tender": {"status": "planning"}, "awards": []}, None, 1),
        ({"tender": {"status": "planning"}, "awards": [], "contracts": []}, None, 1),
    ]
    failing = [
        (
            {"tender": {"status": "planning"}, "awards": [{"title": ""}]},
            {"contracts_count": 0, "awards_count": 1},
            1,
            0,
        ),
        (
            {"tender": {"status": "planning"}, "awards": [], "contracts": [{"title": ""}]},
            {"contracts_count": 1, "awards_count": 0},
            1,
            0,
        ),
    ]
