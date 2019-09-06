
import random

from dataset.distribution import milestone_type

milestone_type = milestone_type.MilestoneTypePathClass()

possible_enums = [
    "b", "c", "d", "e", "f"
]


item_test_undefined1 = {
    "ocid": "1",
    "planning": {
        "milestones": []
    }
}

item_test_undefined2 = {
    "ocid": "2",
    "tender": {
        "milestones": [
            {
                "type": None
            }
        ]
    }
}


def test_undefined():
    scope = {}
    result = milestone_type.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = milestone_type.add_item(scope, {"ocid": "0"}, 0)
    result = milestone_type.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = milestone_type.add_item(scope, item_test_undefined1, 0)
    result = milestone_type.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = milestone_type.add_item(scope, item_test_undefined2, 0)
    result = milestone_type.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }


items_test_passed = [
    {
        "ocid": "1",
        "contracts":
        [
            {
                "implementation": {
                    "milestones": [
                        {
                            "type": "a"
                        }
                    ]
                }
            }
        ]
    }
]


def test_passed():
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = milestone_type.add_item(scope, item, id)
        id += 1

    result = milestone_type.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(milestone_type.important_enums) + 1
    assert result["meta"]["shares"]["a"] == {
        "share": 1.0,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "1"}]
    }


items_test_passed_big_load = [
    {
        "ocid": str(i),
        "tender": {
            "milestones": [
                {
                    "type": random.choice(possible_enums)
                }
            ]
        }
    }
    for i in range(1000)
]


# following test will pass with high probability
def test_passed_big_load():
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = milestone_type.add_item(scope, item, id)
        id += 1

    result = milestone_type.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(possible_enums)
    assert sum(
        [len(value["examples"])
         for _, value in result["meta"]["shares"].items()]
    ) == milestone_type.samples_number * len(possible_enums)
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
