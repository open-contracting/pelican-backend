from dataset.distribution import value
awards_value = value.ModuleType("awards.value")


def test_empty():
    scope = {}
    scope = awards_value.add_item(scope, {}, 1)
    scope = awards_value.add_item(scope, {}, 2)
    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "unsufficient amount of values (at least 100 required)"}


first = {
    "date": "2011-03-28T16:47:36.860000-06:00",
    "awards": [
        {
            "value": {
                "amount": 10000000,
                "currency": "EUR",
            },
        },
    ]
}


second = {
    "date": "2011-03-28T16:47:36.860000-06:00",
    "awards": [
        {
            "value": {
                "amount": 1,
                "currency": "USD",
            },
        },
    ]
}


def test_undefined():
    scope = {}
    scope = awards_value.add_item(scope, first, 1)
    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "unsufficient amount of values (at least 100 required)"}


def test_failed():
    scope = {}
    scope = awards_value.add_item(scope, first, 1)
    for i in range(2, 101):
        scope = awards_value.add_item(scope, second, i)

    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is False
    assert result["value"] is 0
    assert result["meta"] == {
        "counts": {
            "0_1": 1,
            "1_5": 4,
            "20_50": 30,
            "50_100": 50,
            "5_20": 15,
        },
        "shares": {
            "0_1": 14032000,
            "1_5": 4,
            "20_50": 30,
            "50_100": 50,
            "5_20": 15,
        },
        "examples": {
            "0_1": [
                {
                    "abs_amount": 14032000, "item_id": 1, "path": "awards[0].value", "value":
                        {"amount": 10000000, "currency": "EUR"}
                }
            ],
            "1_5": [
                {"abs_amount": 1, "item_id": 2, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 3, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 4, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 5, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
            "5_20": [
                {"abs_amount": 1, "item_id": 6, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 7, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 8, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 9, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 10, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 11, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 12, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 13, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 14, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 15, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
            "20_50": [
                {"abs_amount": 1, "item_id": 21, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 22, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 23, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 24, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 25, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 26, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 27, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 28, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 29, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 30, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
            "50_100": [
                {"abs_amount": 1, "item_id": 51, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 52, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 53, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 54, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 55, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 56, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 57, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 58, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 59, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 60, "path": "awards[0].value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
        },
        "sum": 14032099
    }


def test_ok():
    scope = {}
    for i in range(100):
        scope = awards_value.add_item(scope, second, i + 1)

    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is True
    assert result["value"] is 100
    assert result["meta"] == {
        "counts": {
            "0_1": 1,
            "1_5": 4,
            "5_20": 15,
            "20_50": 30,
            "50_100": 50,
        },
        "shares": {
            "0_1": 1,
            "1_5": 4,
            "5_20": 15,
            "20_50": 30,
            "50_100": 50,
        },
        "examples": {
            "0_1": [
                {"abs_amount": 1, "item_id": 1, "path": "awards[0].value", "value": {"amount": 1, "currency": "USD"}}
            ],
            "1_5": [
                {
                    "abs_amount": 1, "item_id": 2, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 3, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 4, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 5, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
            "5_20": [
                {
                    "abs_amount": 1, "item_id": 6, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 7, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 8, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 9, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 10, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 11, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 12, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 13, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 14, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 15, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
            "20_50": [
                {
                    "abs_amount": 1, "item_id": 21, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 22, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 23, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 24, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 25, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 26, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 27, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 28, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 29, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 30, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
            "50_100": [
                {
                    "abs_amount": 1, "item_id": 51, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 52, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 53, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 54, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 55, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 56, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 57, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 58, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 59, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 60, "path": "awards[0].value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
        },
        "sum": 100
    }