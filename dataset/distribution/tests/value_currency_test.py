
import random

from dataset.distribution import code_distribution

code_distribution = code_distribution.CodeDistribution(
    [
        "tender.value.currency",
        "tender.minValue.currency",
        "awards.value.currency",
        "contracts.value.currency",
        "planning.budget.value.currency",
        "contracts.implementation.transactions.value"
    ]
)

possible_enums = [
    "b", "c", "d", "e", "f"
]


item_test_undefined1 = {
    "ocid": "1",
    "tender": {
        "value": {}
    }
}

item_test_undefined2 = {
    "ocid": "2",
    "tender": {
        "minValue": {
            "currency": None
        }
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
        "ocid": "1",
        "awards":
        [
            {
                "value": {
                    "currency": "a"
                }
            }
        ]
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
    assert result["meta"]["shares"]["a"] == {
        "share": 1.0,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "1"}]
    }


items_test_passed_big_load = [
    {
        "ocid": str(i),
        "contracts": [
            {
                "value": {
                    "currency": random.choice(possible_enums)
                }
            }
        ]
    }
    for i in range(1000)
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
