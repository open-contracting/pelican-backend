
import random

from dataset.distribution import code_distribution

code_distribution = code_distribution.CodeDistribution(
    [
        "awards.status"
    ],
    [
        "active"
    ]
)

possible_enums = [
    "b", "c", "d", "e", "f", "active"
]


item_test_undefined1 = {
    "ocid": "1",
    "awards": {

    }
}

item_test_undefined2 = {
    "ocid": "2",
    "awards": {
        "status": None
    }
}


def test_undefined():
    scope = {}
    result = code_distribution.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = code_distribution.add_item(scope, {"ocid": "0"}, 0)
    result = code_distribution.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = code_distribution.add_item(scope, item_test_undefined1, 0)
    result = code_distribution.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = code_distribution.add_item(scope, item_test_undefined2, 0)
    result = code_distribution.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "there is not a single tender with valid enumeration item"
    }


items_test_passed = [
    {
        "ocid": "0",
        "awards": {
            "status": "active"
        }
    },
    {
        "ocid": "1",
        "awards": {
            "status": "a"
        }
    }
]


def test_passed():
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = code_distribution.add_item(scope, item, id)
        id += 1

    result = code_distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(code_distribution.important_enums) + 1
    assert result["meta"]["shares"]["active"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "0"}]
    }
    assert result["meta"]["shares"]["a"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 1, "ocid": "1"}]
    }


items_test_failed = [
    {
        "ocid": "1",
        "awards": {
            "status": "a"
        }
    }
]


def test_failed():

    scope = {}

    id = 0
    for item in items_test_failed:
        scope = code_distribution.add_item(scope, item, id)
        id += 1

    result = code_distribution.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert len(result["meta"]["shares"]) == len(code_distribution.important_enums) + 1
    assert result["meta"]["shares"]["a"] == {
        "share": 1.0,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "1"}]
    }


items_test_passed_big_load = [
    {
        "ocid": str(i),
        "awards": {
            "status": random.choice(possible_enums)
        }
    }
    for i in range(10000)
]


# following test will pass with high probability
def test_passed_big_load():
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = code_distribution.add_item(scope, item, id)
        id += 1

    result = code_distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(possible_enums)
    assert sum(
        [len(value["examples"])
         for _, value in result["meta"]["shares"].items()]
    ) == code_distribution.samples_number * len(possible_enums)
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
