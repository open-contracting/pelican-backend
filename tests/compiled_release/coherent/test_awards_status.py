import unittest

from contracting_process.resource_level.coherent import awards_status
from tests import CompiledReleaseTests


class TestCase(CompiledReleaseTests, unittest.TestCase):
    module = awards_status
    skipping = [
        (
            {"awards": [{}, {"status": None}, {"status": "active"}, {"status": "pending"}]},
            "no award with an id is inactive",
        )
    ]
    passing = [
        (
            {"awards": [{"status": "pending", "id": 0}]},
            None,
            1,
        ),
        (
            {"awards": [{"status": "pending", "id": 0}], "contracts": [{"awardID": 1}]},
            None,
            1,
        ),
        (
            {
                "awards": [{"status": "pending", "id": 0}, {"status": "pending", "id": 1}],
                "contracts": [{"awardID": 2}, {"awardID": 3}],
            },
            None,
            2,
        ),
    ]
    failing = [
        (
            {"awards": [{"status": "pending", "id": 0}], "contracts": [{"awardID": 0}]},
            {"failed_paths": [{"path": "awards[0]", "id": 0}]},
            1,
            0,
        ),
        (
            {"awards": [{"status": "pending", "id": None}], "contracts": [{"awardID": None}]},
            {"failed_paths": [{"path": "awards[0]", "id": None}]},
            1,
            0,
        ),
        (
            {
                "awards": [{"status": "pending", "id": 0}, {"status": "pending", "id": 1}],
                "contracts": [{"awardID": 1}, {"awardID": 2}],
            },
            {"failed_paths": [{"path": "awards[1]", "id": 1}]},
            2,
            1,
        ),
    ]
