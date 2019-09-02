import random

from dataset.distribution import tender_procurement_method

tender_procurement_method = tender_procurement_method.TenderProcurementMethodPathClass("tender.procurementMethod")


item_test_undefined1 = {
    "tender": {

    }
}

item_test_undefined2 = {
    "tender": {
        "procurementMethod": None
    }
}


def test_undefined():
    scope = {}
    result = tender_procurement_method.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = tender_procurement_method.add_item(scope, {}, 0)
    result = tender_procurement_method.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = tender_procurement_method.add_item(scope, item_test_undefined1, 0)
    result = tender_procurement_method.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = tender_procurement_method.add_item(scope, item_test_undefined2, 0)
    result = tender_procurement_method.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }


items_test_passed = [
    {
        "tender": {
            "procurementMethod": "a"
        }
    },
    {
        "tender": {
            "procurementMethod": "b"
        }
    }
]


def test_passed():
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = tender_procurement_method.add_item(scope, item, id)
        id += 1

    result = tender_procurement_method.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == 2
    assert result["meta"]["shares"]["a"] == {
        "share": 0.5,
        "count": 1,
        "examples_id": [0]
    }
    assert result["meta"]["shares"]["b"] == {
        "share": 0.5,
        "count": 1,
        "examples_id": [1]
    }

items_test_failed = [
    {
        "tender": {
            "procurementMethod": "open"
        }
    }
]


def test_failed():
    scope = {}

    id = 0
    for item in items_test_failed:
        scope = tender_procurement_method.add_item(scope, item, id)
        id += 1

    result = tender_procurement_method.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert len(result["meta"]["shares"]) == 1
    assert result["meta"]["shares"]["open"] == {
        "share": 1,
        "count": 1,
        "examples_id": [0]
    }

possible_status = [
    "open", "b", "c", "d", "e", "f"
]

items_test_passed_big_load = [
    {
        "tender": {
            "procurementMethod": random.choice(possible_status)
        }
    }
    for _ in range(100000)
]


# following test will pass with high probability
def test_passed_big_load():
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = tender_procurement_method.add_item(scope, item, id)
        id += 1

    result = tender_procurement_method.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == 6
    assert sum(
        [len(value["examples_id"]) for _, value in result["meta"]["shares"].items()]
    ) == 20 * 6
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
