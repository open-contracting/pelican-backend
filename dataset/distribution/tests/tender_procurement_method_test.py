import random

from dataset.distribution import code_distribution

code_distribution = code_distribution.CodeDistribution(
    [
        "tender.procurementMethod"
    ],
    [
        "open"
    ]
)


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
    code_distribution.important_enums = ["open"]
    scope = {}
    result = code_distribution.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = code_distribution.add_item(scope, {}, 0)
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
        "tender": {
            "procurementMethod": "a"
        }
    },
    {
        "ocid": "1",
        "tender": {
            "procurementMethod": "b"
        }
    },
    {
        "ocid": "1",
        "tender": {
            "procurementMethod": "c"
        }
    },
    {
        "ocid": "1",
        "tender": {
            "procurementMethod": "open"
        }
    }
]


def test_passed():
    code_distribution.important_enums = ["open"]
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = code_distribution.add_item(scope, item, id)
        id += 1

    result = code_distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(code_distribution.important_enums) + 3
    assert result["meta"]["shares"]["open"] == {
        "share": 1/(len(code_distribution.important_enums) + 3),
        "count": 1,
        "examples": [
            {
                "item_id": 3,
                "ocid": "1"
            }
        ]
    }


items_test_failed = [
    {
        "ocid": "1",
        "tender": {
            "procurementMethod": "open"
        }
    }
]


def test_failed():
    code_distribution.important_enums = ["open"]
    scope = {}

    id = 0
    for item in items_test_failed:
        scope = code_distribution.add_item(scope, item, id)
        id += 1

    result = code_distribution.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert len(result["meta"]["shares"]) == len(code_distribution.important_enums)
    assert result["meta"]["shares"]["open"] == {
        "share": 1,
        "count": 1,
        "examples": [
            {
                "item_id": 0,
                "ocid": "1"
            }
        ]
    }


possible_status = [
    "b", "c", "d", "e", "f"
]

possible_status += code_distribution.important_enums

items_test_passed_big_load = [
    {
        "ocid": "1",
        "tender": {
            "procurementMethod": random.choice(possible_status)
        }
    }
    for _ in range(10000)
]


# following test will pass with high probability
def test_passed_big_load():
    code_distribution.important_enums = ["open"]
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = code_distribution.add_item(scope, item, id)
        id += 1

    result = code_distribution.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(possible_status)
    assert sum(
        [len(value["examples"]) for _, value in result["meta"]["shares"].items()]
    ) == code_distribution.samples_number * len(possible_status)
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
