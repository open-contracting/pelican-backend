from tools.getter import get_values

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
                "quantity": 5.0,
                "inner_list": [{"aaa": "ddd"}, {"aaa": "eee"}]
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
    assert get_values(item, "id") == [{"path": "id", "value": item["id"]}]
    assert get_values(item, "") == [{"path": "", "value": item}]
    assert get_values(item, "tender") == [{"path": "tender", "value": item["tender"]}]
    assert get_values(item, "tender.id") == [{"path": "tender.id", "value": "0rw29R-005-2011-1"}]

    assert get_values(item, "id", value_only=True) == [item["id"]]
    assert get_values(item, "", value_only=True) == [item]
    assert get_values(item, "tender", value_only=True) == [item["tender"]]
    assert get_values(item, "tender.id", value_only=True) == ["0rw29R-005-2011-1"]

    result = get_values(item, "tender.ids")
    assert type(result) is list
    assert(len(result)) == 0

    result = get_values(item, "tender.ids", value_only=True)
    assert type(result) is list
    assert(len(result)) == 0


def test_get_value_lists():
    result = get_values(item, "tender.items.quantity")
    assert result == [
        {"path": "tender.items[0].quantity", "value": 4.0},
        {"path": "tender.items[1].quantity", "value": 5.0},
        {"path": "tender.items[2].quantity", "value": 5.0},
    ]

    assert get_values(item, "tender.items.quantity", value_only=True) == [4.0, 5.0, 5.0]

    assert get_values(item, "tender.items.unit") == [
        {"path": "tender.items[0].unit", "value": {"name": "Unidad"}},
        {"path": "tender.items[2].unit", "value": {"name": "Unimom"}},
    ]

    assert get_values(item, "tender.items.unit", value_only=True) == [{"name": "Unidad"}, {"name": "Unimom"}]

    assert get_values(item, "tender.items.unit.name") == [
        {"path": "tender.items[0].unit.name", "value": "Unidad"},
        {"path": "tender.items[2].unit.name", "value": "Unimom"},
    ]

    assert get_values(item, "tender.items.unit.name", value_only=True) == ["Unidad", "Unimom"]

    result = get_values(item, "tender.items.non_existing")
    assert type(result) is list
    assert len(result) == 0


def test_join():
    assert get_values(item, "tender.items.inner_list.aaa") == [
        {"path": "tender.items[0].inner_list[0].aaa", "value": "bbb"},
        {"path": "tender.items[0].inner_list[1].aaa", "value": "ccc"},
        {"path": "tender.items[1].inner_list[0].aaa", "value": "ddd"},
        {"path": "tender.items[1].inner_list[1].aaa", "value": "eee"},
        {"path": "tender.items[2].inner_list[0].aaa", "value": "ddd"},
        {"path": "tender.items[2].inner_list[1].aaa", "value": "eee"}]

    assert get_values(item, "tender.items.inner_list.aaa", value_only=True) == \
        ["bbb", "ccc", "ddd", "eee", "ddd", "eee"]

    assert get_values(item, "tender.items.inner_list") == [
        {"path": "tender.items[0].inner_list[0]", "value": {"aaa": "bbb"}},
        {"path": "tender.items[0].inner_list[1]", "value": {"aaa": "ccc"}},
        {"path": "tender.items[1].inner_list[0]", "value": {"aaa": "ddd"}},
        {"path": "tender.items[1].inner_list[1]", "value": {"aaa": "eee"}},
        {"path": "tender.items[2].inner_list[0]", "value": {"aaa": "ddd"}},
        {"path": "tender.items[2].inner_list[1]", "value": {"aaa": "eee"}}]

    assert get_values(item, "tender.items.inner_list", value_only=True) == \
        [{"aaa": "bbb"}, {"aaa": "ccc"}, {"aaa": "ddd"}, {"aaa": "eee"}, {"aaa": "ddd"}, {"aaa": "eee"}]


def test_end_of_path():
    result = get_values(item, "tender")
    assert type(result) is list
    assert result == [
        {
            "path": "tender",
            "value": item["tender"]
        }
    ]

    result = get_values(item, "tender", value_only=True)
    assert type(result) is list
    assert result == [
        item["tender"]
    ]

    result = get_values(item, "tender.items")
    assert type(result) is list
    assert len(result) == 3
    assert result == [
        {
            "path": "tender.items[0]",
            "value": item["tender"]["items"][0]
        },
        {
            "path": "tender.items[1]",
            "value": item["tender"]["items"][1]
        },
        {
            "path": "tender.items[2]",
            "value": item["tender"]["items"][2]
        }
    ]

    result = get_values(item, "tender.items", value_only=True)
    assert type(result) is list
    assert len(result) == 3
    assert result == [
        item["tender"]["items"][0],
        item["tender"]["items"][1],
        item["tender"]["items"][2]
    ]
