from dataset.distribution import contracts_value


def test_empty():
    scope = {}
    scope = contracts_value.add_item(scope, {}, 1)
    scope = contracts_value.add_item(scope, {}, 2)
    result = contracts_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "unsufficient amount of contract values (at least 100 required)"}


first = {
    "contracts": [
        {
            "value": {
                "amount": 10000000,
                "currency": "USD",
            },
        },
    ]
}


second = {
    "contracts": [
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
    scope = contracts_value.add_item(scope, first, 1)
    result = contracts_value.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "unsufficient amount of contract values (at least 100 required)"}


def test_failed():
    scope = {}
    scope = contracts_value.add_item(scope, first, 1)
    for i in range(2, 101):
        scope = contracts_value.add_item(scope, second, i)

    result = contracts_value.get_result(scope)
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
            "0_1": 10000000,
            "1_5": 4,
            "20_50": 30,
            "50_100": 50,
            "5_20": 15,
        },
        "examples": {
            "0_1": [
                {'abs_amount': 10000000, 'item_id': 1, 'path': 'contracts[0].value', 'value': {'amount': 10000000, 'currency': 'USD'}}
            ],
            "1_5": [
                {'abs_amount': 1, 'item_id': 2, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 3, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 4, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 5, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
            "5_20": [
                {'abs_amount': 1, 'item_id': 6, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 7, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 8, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 9, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 10, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 11, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 12, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 13, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 14, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 15, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
            "20_50": [
                {'abs_amount': 1, 'item_id': 21, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 22, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 23, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 24, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 25, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 26, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 27, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 28, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 29, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 30, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
            "50_100": [
                {'abs_amount': 1, 'item_id': 51, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 52, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 53, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 54, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 55, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 56, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 57, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 58, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 59, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 60, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
        },
        "sum": 10000099
    }


def test_ok():
    scope = {}
    for i in range(100):
        scope = contracts_value.add_item(scope, second, i + 1)

    result = contracts_value.get_result(scope)
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
                {'abs_amount': 1, 'item_id': 1, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}}
            ],
            "1_5": [
                {'abs_amount': 1, 'item_id': 2, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 3, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 4, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 5, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
            "5_20": [
                {'abs_amount': 1, 'item_id': 6, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 7, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 8, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 9, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 10, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 11, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 12, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 13, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 14, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 15, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
            "20_50": [
                {'abs_amount': 1, 'item_id': 21, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 22, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 23, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 24, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 25, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 26, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 27, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 28, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 29, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 30, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
            "50_100": [
                {'abs_amount': 1, 'item_id': 51, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 52, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 53, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 54, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 55, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 56, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 57, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 58, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 59, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
                {'abs_amount': 1, 'item_id': 60, 'path': 'contracts[0].value', 'value': {'amount': 1, 'currency': 'USD'}},
            ],
        },
        "sum": 100
    }
