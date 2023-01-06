from dataset.distribution import value
from tools.currency_converter import bootstrap

bootstrap()
awards_value = value.ModuleType("awards.value")

item_unset1 = {"ocid": "1"}
item_unset2 = {"ocid": "2"}


def test_empty():
    scope = {}
    scope = awards_value.add_item(scope, item_unset1, 1)
    scope = awards_value.add_item(scope, item_unset2, 2)
    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "insufficient amount of values (at least 100 required)"}


first = {
    "ocid": "1",
    "date": "2019-01-10T22:00:00+01:00",
    "awards": [
        {
            "value": {
                "amount": 10000000,
                "currency": "EUR",
            },
        },
    ],
}


second = {
    "ocid": "1",
    "date": "2019-01-10T22:00:00+01:00",
    "awards": [
        {
            "value": {
                "amount": 1,
                "currency": "USD",
            },
        },
    ],
}


def test_undefined():
    scope = {}
    scope = awards_value.add_item(scope, first, 1)
    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "insufficient amount of values (at least 100 required)"}


def test_failed():
    scope = {}
    scope = awards_value.add_item(scope, first, 1)
    for i in range(2, 101):
        scope = awards_value.add_item(scope, second, i)

    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is False
    assert result["value"] == 0
    assert result["meta"] == {
        "counts": {
            "0_1": 1,
            "1_5": 4,
            "20_50": 30,
            "50_100": 50,
            "5_20": 15,
        },
        "sums": {"0_1": 11507000, "1_5": 4, "20_50": 30, "50_100": 50, "5_20": 15},
        "shares": {
            "0_1": 11507000 / result["meta"]["sum"],
            "1_5": 4 / result["meta"]["sum"],
            "20_50": 30 / result["meta"]["sum"],
            "50_100": 50 / result["meta"]["sum"],
            "5_20": 15 / result["meta"]["sum"],
        },
        "examples": {
            "0_1": [
                {
                    "abs_amount": 11507000,
                    "item_id": 1,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 10000000, "currency": "EUR"},
                }
            ],
            "1_5": [
                {
                    "abs_amount": 1,
                    "item_id": 2,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 3,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 4,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 5,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
            "5_20": [
                {
                    "abs_amount": 1,
                    "item_id": 6,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 7,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 8,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 9,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 10,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 11,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 12,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 13,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 14,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 15,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
            "20_50": [
                {
                    "abs_amount": 1,
                    "item_id": 21,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 22,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 23,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 24,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 25,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 26,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 27,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 28,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 29,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 30,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
            "50_100": [
                {
                    "abs_amount": 1,
                    "item_id": 51,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 52,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 53,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 54,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 55,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 56,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 57,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 58,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 59,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 60,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
        },
        "sum": 11507099,
    }


def test_ok():
    scope = {}
    for i in range(100):
        scope = awards_value.add_item(scope, second, i + 1)

    result = awards_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is True
    assert result["value"] == 100
    assert result["meta"] == {
        "counts": {
            "0_1": 1,
            "1_5": 4,
            "5_20": 15,
            "20_50": 30,
            "50_100": 50,
        },
        "sums": {"0_1": 1, "1_5": 4, "5_20": 15, "20_50": 30, "50_100": 50},
        "shares": {
            "0_1": 1 / result["meta"]["sum"],
            "1_5": 4 / result["meta"]["sum"],
            "5_20": 15 / result["meta"]["sum"],
            "20_50": 30 / result["meta"]["sum"],
            "50_100": 50 / result["meta"]["sum"],
        },
        "examples": {
            "0_1": [
                {
                    "abs_amount": 1,
                    "item_id": 1,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                }
            ],
            "1_5": [
                {
                    "abs_amount": 1,
                    "item_id": 2,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 3,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 4,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 5,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
            "5_20": [
                {
                    "abs_amount": 1,
                    "item_id": 6,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 7,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 8,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 9,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 10,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 11,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 12,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 13,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 14,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 15,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
            "20_50": [
                {
                    "abs_amount": 1,
                    "item_id": 21,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 22,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 23,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 24,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 25,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 26,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 27,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 28,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 29,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 30,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
            "50_100": [
                {
                    "abs_amount": 1,
                    "item_id": 51,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 52,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 53,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 54,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 55,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 56,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 57,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 58,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 59,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
                {
                    "abs_amount": 1,
                    "item_id": 60,
                    "ocid": "1",
                    "path": "awards[0].value",
                    "value": {"amount": 1, "currency": "USD"},
                },
            ],
        },
        "sum": 100,
    }
