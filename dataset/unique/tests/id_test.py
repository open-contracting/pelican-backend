from dataset.unique import id


def test_empty():
    scope = {}
    scope = id.add_item(scope, {}, 1)
    scope = id.add_item(scope, {}, 2)
    result = id.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] is None


first = {"id": "id_1"}
second = {"id": "id_2"}
third = {"id": "id_3"}
fourth = {"id": "id_2"}
fifth = {"id": "id_5"}


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
                "examples": [2, 4]
            },
        }
    }
