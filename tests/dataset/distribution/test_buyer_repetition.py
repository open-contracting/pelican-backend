from dataset.distribution import buyer_repetition
from tests import is_subset_dict

item_unset = {"ocid": "0"}


def test_undefined():
    scope = {}
    result = buyer_repetition.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}

    scope = {}
    scope = buyer_repetition.add_item(scope, item_unset, 0)
    result = buyer_repetition.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}


items_test_passed1 = []
items_test_passed1.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": -1}}} for _ in range(20)])
items_test_passed1.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": num}}} for num in range(980)])

items_test_passed2 = []
items_test_passed2.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": -1}}} for _ in range(490)])
items_test_passed2.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": num}}} for num in range(510)])


def test_passed():
    scope = {}

    for item_id, item in enumerate(items_test_passed1):
        scope = buyer_repetition.add_item(scope, item, item_id)

    result = buyer_repetition.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert result["meta"] == {
        "total_ocid_count": 1000,
        "ocid_count": 20,
        "ocid_share": 20 / 1000,
        "examples": [{"ocid": "0", "item_id": item_id} for item_id in range(20)],
        "specifics": {"buyer.identifier.id": "-1", "buyer.identifier.scheme": "ICO"},
    }

    scope = {}

    for item_id, item in enumerate(items_test_passed2):
        scope = buyer_repetition.add_item(scope, item, item_id)

    result = buyer_repetition.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert is_subset_dict(
        {
            "total_ocid_count": 1000,
            "ocid_count": 490,
            "ocid_share": 490 / 1000,
            "specifics": {"buyer.identifier.id": "-1", "buyer.identifier.scheme": "ICO"},
        },
        result["meta"],
    )


items_test_failed1 = []
items_test_failed1.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": -1}}} for _ in range(10)])
items_test_failed1.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": num}}} for num in range(990)])

items_test_failed2 = []
items_test_failed2.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": -1}}} for _ in range(500)])
items_test_failed2.extend([{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": num}}} for num in range(500)])


def test_failed():
    scope = {}

    for item_id, item in enumerate(items_test_failed1):
        scope = buyer_repetition.add_item(scope, item, item_id)

    result = buyer_repetition.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert result["meta"] == {
        "total_ocid_count": 1000,
        "ocid_count": 10,
        "ocid_share": 10 / 1000,
        "examples": [{"ocid": "0", "item_id": item_id} for item_id in range(10)],
        "specifics": {"buyer.identifier.id": "-1", "buyer.identifier.scheme": "ICO"},
    }

    scope = {}

    for item_id, item in enumerate(items_test_failed2):
        scope = buyer_repetition.add_item(scope, item, item_id)

    result = buyer_repetition.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert is_subset_dict(
        {
            "total_ocid_count": 1000,
            "ocid_count": 500,
            "ocid_share": 500 / 1000,
            "specifics": {"buyer.identifier.id": "-1", "buyer.identifier.scheme": "ICO"},
        },
        result["meta"],
    )
