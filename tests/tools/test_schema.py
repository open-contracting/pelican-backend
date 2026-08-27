import pytest

from pelican.util.schema import get_paths


@pytest.mark.parametrize(
    ("definition", "expected"),
    [
        (
            "Period",
            (
                "tender.tenderPeriod",
                "tender.enquiryPeriod",
                "tender.awardPeriod",
                "tender.contractPeriod",
                "awards.contractPeriod",
                "contracts.period",
            ),
        ),
        (
            # `contracts.implementation.transactions.amount` is deprecated.
            "Value",
            (
                "planning.budget.amount",
                "tender.items.unit.value",
                "tender.value",
                "tender.minValue",
                "awards.value",
                "awards.items.unit.value",
                "contracts.value",
                "contracts.items.unit.value",
                "contracts.implementation.transactions.value",
            ),
        ),
        (
            # Milestone's `documents` field is deprecated.
            "Document",
            (
                "planning.documents",
                "tender.documents",
                "awards.documents",
                "contracts.documents",
                "contracts.implementation.documents",
            ),
        ),
        (
            "Milestone",
            (
                "planning.milestones",
                "tender.milestones",
                "contracts.implementation.milestones",
                "contracts.milestones",
            ),
        ),
        ("RelatedProcess", ("contracts.relatedProcesses", "relatedProcesses")),
        ("Item", ("tender.items", "awards.items", "contracts.items")),
        # `amendment` fields are deprecated.
        ("Amendment", ("tender.amendments", "awards.amendments", "contracts.amendments")),
    ],
)
def test_get_paths(definition, expected):
    assert get_paths(definition) == expected


def test_get_paths_unknown():
    assert get_paths("Nonexistent") == ()
