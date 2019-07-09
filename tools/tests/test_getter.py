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


def test_get_value_lists():
    assert get_values(item, "tender.items.quantity") == [
        {"path": "tender.items[0].quantity", "value": 4.0},
        {"path": "tender.items[1].quantity", "value": 5.0},
        {"path": "tender.items[2].quantity", "value": 5.0},
    ]

    assert get_values(item, "tender.items.unit") == [
        {"path": "tender.items[0].unit", "value": {"name": "Unidad"}},
        {"path": "tender.items[2].unit", "value": {"name": "Unimom"}},
    ]

    assert get_values(item, "tender.items.unit.name") == [
        {"path": "tender.items[0].unit.name", "value": "Unidad"},
        {"path": "tender.items[2].unit.name", "value": "Unimom"},
    ]


def test_join():
    assert get_values(item, "tender.items.inner_list.aaa") == [
        {'path': 'tender.items[0].inner_list[0].aaa', 'value': 'bbb'},
        {'path': 'tender.items[0].inner_list[1].aaa', 'value': 'ccc'},
        {'path': 'tender.items[1].inner_list[0].aaa', 'value': 'ddd'},
        {'path': 'tender.items[1].inner_list[1].aaa', 'value': 'eee'},
        {'path': 'tender.items[2].inner_list[0].aaa', 'value': 'ddd'},
        {'path': 'tender.items[2].inner_list[1].aaa', 'value': 'eee'}]

    assert get_values(item, "tender.items.inner_list") == [
        {'path': 'tender.items[0].inner_list', 'value': [{"aaa": "bbb"}, {"aaa": "ccc"}]},
        {'path': 'tender.items[1].inner_list', 'value': [{"aaa": "ddd"}, {"aaa": "eee"}]},
        {'path': 'tender.items[2].inner_list', 'value': [{"aaa": "ddd"}, {"aaa": "eee"}]}]
