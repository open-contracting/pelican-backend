
import random

from dataset.distribution import value_currency

value_currency = value_currency.ValueCurrencyPathClass()

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
    result = value_currency.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = value_currency.add_item(scope, {"ocid": "0"}, 0)
    result = value_currency.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = value_currency.add_item(scope, item_test_undefined1, 0)
    result = value_currency.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = value_currency.add_item(scope, item_test_undefined2, 0)
    result = value_currency.get_result(scope)
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
        scope = value_currency.add_item(scope, item, id)
        id += 1

    result = value_currency.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(value_currency.important_enums) + 1
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
        scope = value_currency.add_item(scope, item, id)
        id += 1

    result = value_currency.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(possible_enums)
    assert sum(
        [len(value["examples"])
         for _, value in result["meta"]["shares"].items()]
    ) == value_currency.samples_number * len(possible_enums)
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
