from dataset.distribution import tender_value


def test_empty():
    scope = {}
    scope = tender_value.add_item(scope, {}, 1)
    scope = tender_value.add_item(scope, {}, 2)
    result = tender_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "unsufficient amount of values (at least 100 required)"}


first = {
    "date": "2011-03-28T16:47:36.860000-06:00",
    "tender":
        {
            "value": {
                "amount": 10000000,
                "currency": "EUR",
            },
        },
}


second = {
    "date": "2011-03-28T16:47:36.860000-06:00",
    "tender":
        {
            "value": {
                "amount": 1,
                "currency": "USD",
            },
        },

}


def test_undefined():
    scope = {}
    scope = tender_value.add_item(scope, first, 1)
    result = tender_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "unsufficient amount of values (at least 100 required)"}


def test_failed():
    scope = {}
    scope = tender_value.add_item(scope, first, 1)
    for i in range(2, 101):
        scope = tender_value.add_item(scope, second, i)

    result = tender_value.get_result(scope)
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
                    "abs_amount": 14032000, "item_id": 1, "path": "tender.value", "value":
                        {"amount": 10000000, "currency": "EUR"}
                }
            ],
            "1_5": [
                {"abs_amount": 1, "item_id": 2, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 3, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 4, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 5, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
            "5_20": [
                {"abs_amount": 1, "item_id": 6, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 7, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 8, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 9, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 10, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 11, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 12, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 13, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 14, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 15, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
            "20_50": [
                {"abs_amount": 1, "item_id": 21, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 22, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 23, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 24, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 25, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 26, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 27, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 28, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 29, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 30, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
            "50_100": [
                {"abs_amount": 1, "item_id": 51, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 52, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 53, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 54, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 55, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 56, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 57, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 58, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 59, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
                {"abs_amount": 1, "item_id": 60, "path": "tender.value", "value":
                    {"amount": 1, "currency": "USD"}},
            ],
        },
        "sum": 14032099
    }


def test_ok():
    scope = {}
    for i in range(100):
        scope = tender_value.add_item(scope, second, i + 1)

    result = tender_value.get_result(scope)
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
                {"abs_amount": 1, "item_id": 1, "path": "tender.value", "value": {"amount": 1, "currency": "USD"}}
            ],
            "1_5": [
                {
                    "abs_amount": 1, "item_id": 2, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 3, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 4, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 5, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
            "5_20": [
                {
                    "abs_amount": 1, "item_id": 6, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 7, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 8, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 9, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 10, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 11, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 12, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 13, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 14, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 15, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
            "20_50": [
                {
                    "abs_amount": 1, "item_id": 21, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 22, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 23, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 24, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 25, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 26, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 27, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 28, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 29, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 30, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
            "50_100": [
                {
                    "abs_amount": 1, "item_id": 51, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 52, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 53, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 54, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 55, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 56, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 57, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 58, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 59, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
                {
                    "abs_amount": 1, "item_id": 60, "path": "tender.value", "value":
                        {"amount": 1, "currency": "USD"}
                },
            ],
        },
        "sum": 100
    }
