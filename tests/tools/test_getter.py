from tools.getter import get_values

item = {
    "id": "123",
    "tender": {
        "id": "0rw29R-005-2011-1",
        "items": [
            {"unit": {"name": "Unidad"}, "quantity": 4.0, "additionalClassifications": [{"id": "bbb"}, {"id": "ccc"}]},
            {"quantity": 5.0, "additionalClassifications": [{"id": "ddd"}, {"id": "eee"}]},
            {"unit": {"name": "Unimom"}, "quantity": 5.0, "additionalClassifications": [{"id": "ddd"}, {"id": "eee"}]},
        ],
        "milestones": [{"status": None}],
    },
    "contracts": [{"documents": [{"id": 0}, {"id": 1}]}, {"documents": [{"id": 2}]}],
}


def test_get_values_invalid():
    assert get_values({"tender": {"tenderers": "string"}}, "tender.tenderers.contactPoint.name") == []


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
    assert (len(result)) == 0

    result = get_values(item, "tender.ids", value_only=True)
    assert type(result) is list
    assert (len(result)) == 0


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
    assert get_values(item, "tender.items.additionalClassifications.id") == [
        {"path": "tender.items[0].additionalClassifications[0].id", "value": "bbb"},
        {"path": "tender.items[0].additionalClassifications[1].id", "value": "ccc"},
        {"path": "tender.items[1].additionalClassifications[0].id", "value": "ddd"},
        {"path": "tender.items[1].additionalClassifications[1].id", "value": "eee"},
        {"path": "tender.items[2].additionalClassifications[0].id", "value": "ddd"},
        {"path": "tender.items[2].additionalClassifications[1].id", "value": "eee"},
    ]

    assert get_values(item, "tender.items.additionalClassifications.id", value_only=True) == [
        "bbb",
        "ccc",
        "ddd",
        "eee",
        "ddd",
        "eee",
    ]

    assert get_values(item, "tender.items.additionalClassifications") == [
        {"path": "tender.items[0].additionalClassifications[0]", "value": {"id": "bbb"}},
        {"path": "tender.items[0].additionalClassifications[1]", "value": {"id": "ccc"}},
        {"path": "tender.items[1].additionalClassifications[0]", "value": {"id": "ddd"}},
        {"path": "tender.items[1].additionalClassifications[1]", "value": {"id": "eee"}},
        {"path": "tender.items[2].additionalClassifications[0]", "value": {"id": "ddd"}},
        {"path": "tender.items[2].additionalClassifications[1]", "value": {"id": "eee"}},
    ]

    assert get_values(item, "tender.items.additionalClassifications", value_only=True) == [
        {"id": "bbb"},
        {"id": "ccc"},
        {"id": "ddd"},
        {"id": "eee"},
        {"id": "ddd"},
        {"id": "eee"},
    ]


def test_end_of_path():
    result = get_values(item, "tender")
    assert type(result) is list
    assert result == [{"path": "tender", "value": item["tender"]}]

    result = get_values(item, "tender", value_only=True)
    assert type(result) is list
    assert result == [item["tender"]]

    result = get_values(item, "tender.items")
    assert type(result) is list
    assert len(result) == 3
    assert result == [
        {"path": "tender.items[0]", "value": item["tender"]["items"][0]},
        {"path": "tender.items[1]", "value": item["tender"]["items"][1]},
        {"path": "tender.items[2]", "value": item["tender"]["items"][2]},
    ]

    result = get_values(item, "tender.items", value_only=True)
    assert type(result) is list
    assert len(result) == 3
    assert result == [item["tender"]["items"][0], item["tender"]["items"][1], item["tender"]["items"][2]]


def test_indexing():
    result = get_values(item, "tender.items[0]")
    assert type(result) is list
    assert len(result) == 1
    assert result == [{"path": "tender.items[0]", "value": item["tender"]["items"][0]}]

    result = get_values(item, "tender.items[0]", value_only=True)
    assert type(result) is list
    assert len(result) == 1
    assert result == [item["tender"]["items"][0]]

    result = get_values(item, "contracts.documents[0]")
    assert type(result) is list
    assert len(result) == 2
    assert result == [
        {"path": "contracts[0].documents[0]", "value": item["contracts"][0]["documents"][0]},
        {"path": "contracts[1].documents[0]", "value": item["contracts"][1]["documents"][0]},
    ]

    result = get_values(item, "contracts.documents[0]", value_only=True)
    assert type(result) is list
    assert len(result) == 2
    assert result == [item["contracts"][0]["documents"][0], item["contracts"][1]["documents"][0]]

    result = get_values(item, "contracts.documents[1]")
    assert type(result) is list
    assert len(result) == 1
    assert result == [{"path": "contracts[0].documents[1]", "value": item["contracts"][0]["documents"][1]}]

    result = get_values(item, "contracts.documents[1]", value_only=True)
    assert type(result) is list
    assert len(result) == 1
    assert result == [item["contracts"][0]["documents"][1]]

    result = get_values(item, "contracts[0].documents")
    assert type(result) is list
    assert len(result) == 2
    assert result == [
        {"path": "contracts[0].documents[0]", "value": item["contracts"][0]["documents"][0]},
        {"path": "contracts[0].documents[1]", "value": item["contracts"][0]["documents"][1]},
    ]

    result = get_values(item, "contracts[0].documents", value_only=True)
    assert type(result) is list
    assert len(result) == 2
    assert result == [item["contracts"][0]["documents"][0], item["contracts"][0]["documents"][1]]


def test_none_value():
    result = get_values(item, "tender.milestones.status")
    assert type(result) is list
    assert len(result) == 1
    assert result == [{"path": "tender.milestones[0].status", "value": item["tender"]["milestones"][0]["status"]}]

    result = get_values(item, "tender.milestones.status", value_only=True)
    assert type(result) is list
    assert len(result) == 1
    assert result == [item["tender"]["milestones"][0]["status"]]
