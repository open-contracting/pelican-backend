import unittest

from contracting_process.resource_level.coherent import contracts_status
from tests import CompiledReleaseTests


class TestCase(CompiledReleaseTests, unittest.TestCase):
    module = contracts_status
    skipping = [
        (
            {"contracts": [{}, {"status": None}, {"status": "active"}, {"status": "terminated"}]},
            "no contract is unsigned",
        )
    ]
    passing = [
        (
            {
                "contracts": [
                    {},
                    {"status": "pending"},
                    {"status": "cancelled", "implementation": {}},
                    {"status": "pending", "implementation": {"transactions": []}},
                ]
            },
            None,
            3,
        ),
    ]
    failing = [
        (
            {"contracts": [{"status": "pending", "implementation": {"transactions": [{"id": 0}]}}]},
            {"failed_paths": [{"path": "contracts[0]", "transactions_count": 1}]},
            1,
            0,
        ),
        (
            {
                "contracts": [
                    {},
                    {"status": "pending", "implementation": {"transactions": []}},
                    {"status": "cancelled", "implementation": {"transactions": [{"id": 0}, {"id": 1}]}},
                ]
            },
            {"failed_paths": [{"path": "contracts[2]", "transactions_count": 2}]},
            2,
            1,
        ),
    ]
