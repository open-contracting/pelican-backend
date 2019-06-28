from contracting_process.processor import get_value

item = {
    "id": "123",
    "tender": {
        "id": "0rw29R-005-2011-1",
        "items": [
            {
                "unit": {"name": "Unidad"},
                "quantity": 4.0,
                "inner_list": [{"aaa": "bbb"}, {"aaa": "ccc"}]
            },
            {
                "unit": {"name": "Unimom"},
                "quantity": 5.0,
                "inner_list": [{"aaa": "ddd"}, {"aaa": "eee"}]
            },
        ],
    }
}


def test_get_value_simple():
    assert get_value(item, ["id"]) == "123"
    assert get_value(item, [""]) == item
    assert get_value(item, ["tender"]) == item["tender"]
    assert get_value(item, ["tender", "id"]) == "0rw29R-005-2011-1"
    assert get_value(item, ["tender", "id"]) == item["tender"]["id"]


def test_get_value_lists():
    assert get_value(item, ["tender", "items", "quantity"]) == [4.0, 5.0]
    assert get_value(item, ["tender", "items", "unit"]) == [{"name": "Unidad"}, {"name": "Unimom"}]
    assert get_value(item, ["tender", "items", "unit", "name"]) == ["Unidad", "Unimom"]


def test_join():
    assert get_value(item, ["tender", "items", "inner_list", "aaa"]) == [["bbb", "ccc"], ["ddd", "eee"]]
    assert get_value(item, ["tender", "items", "inner_list", "aaa"], simplify=True) == ["bbb", "ccc", "ddd", "eee"]

    assert get_value(item, ["tender", "items", "inner_list"], simplify=True) == [
        {"aaa": "bbb"}, {"aaa": "ccc"}, {"aaa": "ddd"}, {"aaa": "eee"}]
    assert get_value(item, ["tender", "items", "inner_list"]) == [
        [{"aaa": "bbb"}, {"aaa": "ccc"}], [{"aaa": "ddd"}, {"aaa": "eee"}]]
