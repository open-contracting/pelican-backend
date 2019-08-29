from dataset.unique import id


def test_empty():
    scope = {}
    scope = id.add_item(scope, {"ocid": "1"}, 1)
    scope = id.add_item(scope, {"ocid": "2"}, 2)
    result = id.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] is None


first = {
    "ocid": "1",
    "id": "id_1"
}
second = {
    "ocid": "2",
    "id": "id_2"
}
third = {
    "ocid": "3",
    "id": "id_3"
}
fourth = {
    "ocid": "4",
    "id": "id_2"
}
fifth = {
    "ocid": "5",
    "id": "id_5"
}


def test_ok():
    scope = {}
    scope = id.add_item(scope, first, 1)
    scope = id.add_item(scope, second, 2)
    scope = id.add_item(scope, third, 3)
    result = id.get_result(scope)
    assert type(result) == dict
    assert result["result"] is True
    assert result["value"] is 100
    assert result["meta"] is None


def test_failed():
    scope = {}
    scope = id.add_item(scope, second, 2)
    scope = id.add_item(scope, third, 3)
    scope = id.add_item(scope, fourth, 4)
    result = id.get_result(scope)
    assert type(result) == dict
    assert result["result"] is False
    assert result["value"] is 0
    assert result["meta"] == {
        "failed": {
            "id_2": {
                "count": 2,
                "examples": [{"item_id": 2, "ocid": "2"}, {"item_id": 4, "ocid": "4"}]
            },
        }
    }
