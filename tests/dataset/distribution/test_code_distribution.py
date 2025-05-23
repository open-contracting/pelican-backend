from dataset.distribution.code_distribution import CodeDistribution
from tests import is_subset_dict

items_multiple_items = [
    {"ocid": "0", "awards": [{"status": "pending"}, {"status": "pending"}, {"status": "active"}]},
    {"ocid": "1", "awards": [{"status": "active"}]},
]

items_complex_structure = [
    {
        "ocid": "0",
        "contracts": [
            {"implementation": {"milestones": [{"status": "met"}, {"status": "met"}]}},
            {"implementation": {"milestones": [{"status": "notMet"}, {"status": "notMet"}]}},
        ],
    }
]

items_multiple_paths = [
    {
        "ocid": "0",
        "planning": {"documents": [{"documentType": "pending"}]},
        "tender": {"documents": [{"documentType": "active"}]},
    }
]


def test_no_test_values():
    # items_multiple_items
    distribution = CodeDistribution(["awards.status"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_multiple_items):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert is_subset_dict({"share": 0.5, "count": 2}, result["meta"]["shares"]["pending"])
    assert len(result["meta"]["shares"]["pending"]["examples"]) == 2
    assert is_subset_dict({"share": 0.5, "count": 2}, result["meta"]["shares"]["active"])
    assert len(result["meta"]["shares"]["active"]["examples"]) == 2

    # items_complex_structure
    distribution = CodeDistribution(["contracts.implementation.milestones.status"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_complex_structure):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert is_subset_dict({"share": 0.5, "count": 2}, result["meta"]["shares"]["met"])
    assert len(result["meta"]["shares"]["met"]["examples"]) == 2
    assert is_subset_dict({"share": 0.5, "count": 2}, result["meta"]["shares"]["notMet"])
    assert len(result["meta"]["shares"]["notMet"]["examples"]) == 2

    # items_multiple_paths
    distribution = CodeDistribution(["planning.documents.documentType", "tender.documents.documentType"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_multiple_paths):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert result["meta"] == {
        "shares": {
            "pending": {"share": 0.5, "count": 1, "examples": [{"ocid": "0", "item_id": 0}]},
            "active": {"share": 0.5, "count": 1, "examples": [{"ocid": "0", "item_id": 0}]},
        }
    }


items_passed1 = [
    {
        "ocid": "0",
        "awards": [{"status": "pending"}, {"status": "active"}, {"status": "cancelled"}, {"status": "unsuccessful"}],
    }
]

items_passed2 = [{"ocid": "0", "awards": [{"status": "pending"}]}]
items_passed2.extend([{"ocid": "0", "awards": [{"status": "active"}]} for i in range(999)])

items_passed3 = [{"ocid": "0", "awards": [{"status": "pending"}]}]
items_passed3.extend([{"ocid": "0", "awards": [{"status": "active"}]} for i in range(99)])


def test_passed():
    # test_passed1
    distribution = CodeDistribution(["awards.status"], ["pending", "active", "cancelled", "unsuccessful"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_passed1):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert result["meta"] == {
        "shares": {
            "pending": {"share": 1 / 4, "count": 1, "examples": [{"ocid": "0", "item_id": 0}]},
            "active": {"share": 1 / 4, "count": 1, "examples": [{"ocid": "0", "item_id": 0}]},
            "cancelled": {"share": 1 / 4, "count": 1, "examples": [{"ocid": "0", "item_id": 0}]},
            "unsuccessful": {"share": 1 / 4, "count": 1, "examples": [{"ocid": "0", "item_id": 0}]},
        }
    }

    # test_passed2
    distribution = CodeDistribution(["awards.status"], ["pending"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_passed2):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert is_subset_dict({"share": 1 / 1000, "count": 1}, result["meta"]["shares"]["pending"])
    assert len(result["meta"]["shares"]["pending"]["examples"]) == 1
    assert is_subset_dict({"share": 999 / 1000, "count": 999}, result["meta"]["shares"]["active"])
    assert len(result["meta"]["shares"]["active"]["examples"]) == 20

    # test_passed3
    distribution = CodeDistribution(["awards.status"], ["pending", "active"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_passed3):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert is_subset_dict({"share": 1 / 100, "count": 1}, result["meta"]["shares"]["pending"])
    assert len(result["meta"]["shares"]["pending"]["examples"]) == 1
    assert is_subset_dict({"share": 99 / 100, "count": 99}, result["meta"]["shares"]["active"])
    assert len(result["meta"]["shares"]["active"]["examples"]) == 20


items_failed1 = [{"ocid": "0", "awards": [{"status": "pending"}]}]

items_failed2 = [{"ocid": "0", "awards": [{"status": "pending"}]}]
items_failed2.extend([{"ocid": "0", "awards": [{"status": "active"}]} for i in range(1000)])

items_failed3 = [{"ocid": "0", "awards": [{"status": "active"}]}]


def test_failed():
    # test_failed1
    distribution = CodeDistribution(["awards.status"], ["pending"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_failed1):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert result["meta"] == {
        "shares": {"pending": {"share": 1.0, "count": 1, "examples": [{"ocid": "0", "item_id": 0}]}}
    }

    # test_failed2
    distribution = CodeDistribution(["awards.status"], ["pending"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_failed2):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert is_subset_dict({"share": 1 / 1001, "count": 1}, result["meta"]["shares"]["pending"])
    assert len(result["meta"]["shares"]["pending"]["examples"]) == 1
    assert is_subset_dict({"share": 1000 / 1001, "count": 1000}, result["meta"]["shares"]["active"])
    assert len(result["meta"]["shares"]["active"]["examples"]) == 20

    # test_failed2
    distribution = CodeDistribution(["awards.status"], ["pending"], limit=20)
    scope = {}
    for item_id, item in enumerate(items_failed3):
        scope = distribution.add_item(scope, item, item_id)

    result = distribution.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
