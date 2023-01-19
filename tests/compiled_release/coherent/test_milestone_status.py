import unittest

from contracting_process.resource_level.coherent import milestone_status
from tests import CompiledReleaseTests


class TestCase(CompiledReleaseTests, unittest.TestCase):
    module = milestone_status
    skipping = [
        (
            {},
            "no milestone is unmet",
        ),
        (
            {"tender": {"milestones": [{}]}},
            "no milestone is unmet",
        ),
    ]
    passing = [
        (
            {
                "tender": {"milestones": [{"title": "some_milestone", "status": "notMet"}]},
                "planning": {"milestones": [{"title": "some_milestone", "status": "notMet"}]},
                "contracts": [
                    {
                        "milestones": [{"title": "some_milestone", "status": "notMet"}],
                        "implementation": {"milestones": [{"title": "some_milestone", "status": "notMet"}]},
                    }
                ],
            },
            None,
            4,
        ),
        (
            {
                "contracts": [
                    {
                        "milestones": [
                            {"title": "some_milestone", "status": "notMet"},
                            {"title": "some_another_milestone", "status": "notMet"},
                        ]
                    },
                    {
                        "milestones": [
                            {"title": "some_milestone", "status": "notMet"},
                            {"title": "some_another_milestone", "status": "notMet"},
                        ]
                    },
                ],
            },
            None,
            4,
        ),
    ]
    failing = [
        (
            {  # invalid
                "tender": {
                    "milestones": [
                        {"title": "some_milestone", "status": "scheduled", "dateMet": {"some": "thing"}},
                        {"title": "some_milestone", "status": "scheduled", "dateMet": {}},
                    ]
                },
                "planning": {
                    "milestones": [
                        {"title": "some_milestone", "status": None},
                        {"title": "some_milestone", "status": "met"},
                    ]
                },
                "contracts": [
                    {
                        "milestones": [{"title": "some_milestone", "status": "notMet"}],
                        "implementation": {"milestones": [{"title": "some_milestone", "status": "notMet"}]},
                    }
                ],
            },
            {"failed_paths": [{"path": "tender.milestones[0]", "status": "scheduled"}]},
            4,
            3,
        ),
    ]
