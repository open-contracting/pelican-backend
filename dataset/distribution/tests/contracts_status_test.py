
import random

from dataset.distribution import contracts_status

contracts_status = contracts_status.ContractsStatusPathClass()

possible_enums = [
    "b", "c", "d", "e", "f", "active", "terminated"
]


item_test_undefined1 = {
    "ocid": "1",
    "contracts": {

    }
}

item_test_undefined2 = {
    "ocid": "2",
    "contracts": {
        "status": None
    }
}


def test_undefined():
    scope = {}
    result = contracts_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = contracts_status.add_item(scope, {"ocid": "0"}, 0)
    result = contracts_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = contracts_status.add_item(scope, item_test_undefined1, 0)
    result = contracts_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = contracts_status.add_item(scope, item_test_undefined2, 0)
    result = contracts_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "there is not a single tender with valid enumeration item"
    }


items_test_passed = [
    {
        "ocid": "0",
        "contracts": {
            "status": "active"
        }
    },
    {
        "ocid": "1",
        "contracts": {
            "status": "terminated"
        }
    }
]


def test_passed():
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = contracts_status.add_item(scope, item, id)
        id += 1

    result = contracts_status.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(contracts_status.important_enums)
    assert result["meta"]["shares"]["active"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "0"}]
    }
    assert result["meta"]["shares"]["terminated"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 1, "ocid": "1"}]
    }


items_test_failed = [
    {
        "ocid": "1",
        "contracts": {
            "status": "a"
        }
    }
]


def test_failed():

    scope = {}

    id = 0
    for item in items_test_failed:
        scope = contracts_status.add_item(scope, item, id)
        id += 1

    result = contracts_status.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert len(result["meta"]["shares"]) == len(contracts_status.important_enums) + 1
    assert result["meta"]["shares"]["a"] == {
        "share": 1.0,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "1"}]
    }


items_test_passed_big_load = [
    {
        "ocid": str(i),
        "contracts": {
            "status": random.choice(possible_enums)
        }
    }
    for i in range(1000)
]


# following test will pass with high probability
def test_passed_big_load():
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = contracts_status.add_item(scope, item, id)
        id += 1

    result = contracts_status.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(possible_enums)
    assert sum(
        [len(value["examples"])
         for _, value in result["meta"]["shares"].items()]
    ) == contracts_status.samples_number * len(possible_enums)
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
