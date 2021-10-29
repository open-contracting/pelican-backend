import unittest

from contracting_process.resource_level.coherent import awards_status
from tests import CompiledReleaseTests


class TestCase(CompiledReleaseTests, unittest.TestCase):
    module = awards_status
    skipping = [
        (
            {"awards": [{}, {"status": None}, {"status": "active"}]},
            "criteria not met",
        )
    ]
    passing = [
        (
            {"awards": [{"status": "pending", "id": 0}]},
            {"processed_awards": [{"path": "awards[0]", "id": 0, "result": True}]},
            1,
        ),
        (
            {"awards": [{"status": "pending", "id": 0}], "contracts": [{"awardID": 1}]},
            {"processed_awards": [{"path": "awards[0]", "id": 0, "result": True}]},
            1,
        ),
        (
            {
                "awards": [{"status": "pending", "id": 0}, {"status": "pending", "id": 1}],
                "contracts": [{"awardID": 2}, {"awardID": 3}],
            },
            {
                "processed_awards": [
                    {"path": "awards[0]", "id": 0, "result": True},
                    {"path": "awards[1]", "id": 1, "result": True},
                ]
            },
            2,
        ),
    ]
    failing = [
        (
            {"awards": [{"status": "pending", "id": 0}], "contracts": [{"awardID": 0}]},
            {"processed_awards": [{"path": "awards[0]", "id": 0, "result": False}]},
            1,
            0,
        ),
        (
            {
                "awards": [{"status": "pending", "id": 0}, {"status": "pending", "id": 1}],
                "contracts": [{"awardID": 1}, {"awardID": 2}],
            },
            {
                "processed_awards": [
                    {"path": "awards[0]", "id": 0, "result": True},
                    {"path": "awards[1]", "id": 1, "result": False},
                ]
            },
            2,
            1,
        ),
    ]
