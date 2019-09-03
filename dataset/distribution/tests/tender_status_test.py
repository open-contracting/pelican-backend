
import random

from dataset.distribution import tender_status

tender_status = tender_status.TenderStatusPathClass()

possible_enums = [
    "b", "c", "d", "e", "f", "planning", "active"
]


item_test_undefined1 = {
    "ocid": "1",
    "tender": {

    }
}

item_test_undefined2 = {
    "ocid": "2",
    "tender": {
        "status": None
    }
}


def test_undefined():
    tender_status.important_enums = [
        "planning", "active"
    ]
    scope = {}
    result = tender_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = tender_status.add_item(scope, {"ocid": "0"}, 0)
    result = tender_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = tender_status.add_item(scope, item_test_undefined1, 0)
    result = tender_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "no data items were processed"
    }

    scope = {}
    scope = tender_status.add_item(scope, item_test_undefined2, 0)
    result = tender_status.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {
        "reason": "there is not a single tender with valid enumeration item"
    }


items_test_passed = [
    {
        "ocid": "0",
        "tender": {
            "status": "active"
        }
    },
    {
        "ocid": "1",
        "tender": {
            "status": "planning"
        }
    }
]


def test_passed():
    tender_status.important_enums = {
        "active", "planning"
    }
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = tender_status.add_item(scope, item, id)
        id += 1

    result = tender_status.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(tender_status.important_enums)
    assert result["meta"]["shares"]["active"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "0"}]
    }
    assert result["meta"]["shares"]["planning"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 1, "ocid": "1"}]
    }


items_test_failed = [
    {
        "ocid": "0",
        "tender": {
            "status": "active"
        }
    },
    {
        "ocid": "1",
        "tender": {
            "status": "unknown"
        }
    }
]


def test_failed():

    scope = {}

    id = 0
    for item in items_test_failed:
        scope = tender_status.add_item(scope, item, id)
        id += 1

    result = tender_status.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert len(result["meta"]["shares"]) == len(tender_status.important_enums) + 1
    assert result["meta"]["shares"]["active"] == {
        "share": 0.5,
        "count": 1,
        "examples": [{"item_id": 0, "ocid": "0"}]
    }
    assert result["meta"]["shares"]["planning"] == {
        "share": 0,
        "count": 0,
        "examples": []
    }
    assert result['meta']['shares']['planning'] == {
        'share': 0,
        'count': 0,
        'examples': []
    }


items_test_passed_big_load = [
    {
        "ocid": str(i),
        "tender": {
            "status": random.choice(possible_enums)
        }
    }
    for i in range(1000)
]


# following test will pass with high probability
def test_passed_big_load():
    tender_status.important_enums = [
        "planning", "active"
    ]

    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = tender_status.add_item(scope, item, id)
        id += 1

    result = tender_status.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(possible_enums)
    assert sum(
        [len(value["examples"])
         for _, value in result["meta"]["shares"].items()]
    ) == tender_status.samples_number * len(possible_enums)
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
