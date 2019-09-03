import random

from dataset.distribution import tender_procurement_method

tender_procurement_method = tender_procurement_method.TenderProcurementMethodPathClass()


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
    tender_procurement_method.important_enums = ["open"]
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
    tender_procurement_method.important_enums = ["open"]
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = tender_procurement_method.add_item(scope, item, id)
        id += 1

    result = tender_procurement_method.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(tender_procurement_method.important_enums) + 3
    assert result["meta"]["shares"]["open"] == {
        "share": 1/(len(tender_procurement_method.important_enums) + 3),
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
    tender_procurement_method.important_enums = ["open"]
    scope = {}

    id = 0
    for item in items_test_failed:
        scope = tender_procurement_method.add_item(scope, item, id)
        id += 1

    result = tender_procurement_method.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert len(result["meta"]["shares"]) == len(tender_procurement_method.important_enums)
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

possible_status += tender_procurement_method.important_enums

items_test_passed_big_load = [
    {
        "ocid": "1",
        "tender": {
            "procurementMethod": random.choice(possible_status)
        }
    }
    for _ in range(100000)
]


# following test will pass with high probability
def test_passed_big_load():
    tender_procurement_method.important_enums = ["open"]
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = tender_procurement_method.add_item(scope, item, id)
        id += 1

    result = tender_procurement_method.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["shares"]) == len(possible_status)
    assert sum(
        [len(value["examples"]) for _, value in result["meta"]["shares"].items()]
    ) == tender_procurement_method.samples_number * len(possible_status)
    assert all(
        [0 < value["share"] < 1 for _, value in result["meta"]["shares"].items()]
    )
