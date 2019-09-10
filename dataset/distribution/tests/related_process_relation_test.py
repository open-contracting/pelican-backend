import random

from dataset.distribution import code_distribution

code_distribution = code_distribution.CodeDistribution(
    [
        "relatedProcess.relationship"
    ]
)

possible_enums = [
    "b", "c", "d", "e", "f"
]


item_test_undefined1 = {
    "ocid": "1",
    "relatedProcess": {

    }
}

item_test_undefined2 = {
    "ocid": "2",
    "relatedProcess": {
        "relationship": None
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
        "reason": "no data items were processed"
    }


items_test_passed = [
    {
        "ocid": "0",
        "relatedProcess": {
            "relationship": "a"
        }
    },
    {
        "ocid": "1",
        "relatedProcess": {
            "relationship": "b"
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
    assert len(result["meta"]["shares"]) == len(items_test_passed)
    assert result["meta"]["shares"]["a"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "0"}]
    }
    assert result["meta"]["shares"]["b"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 1, "ocid": "1"}]
    }


items_test_passed_big_load = [
    {
        "ocid": str(i),
        "relatedProcess": {
            "relationship": random.choice(possible_enums)
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
