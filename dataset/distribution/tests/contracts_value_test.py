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
    for i in range(99):
        scope = contracts_value.add_item(scope, second, i + 1)

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
            "5_20": 15
        },
        "shares": {
            "0_1": 10000000,
            "1_5": 4,
            "20_50": 30,
            "50_100": 50,
            "5_20": 15
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
            "20_50": 30,
            "50_100": 50,
            "5_20": 15
        },
        "shares": {
            "0_1": 1,
            "1_5": 4,
            "20_50": 30,
            "50_100": 50,
            "5_20": 15
        },
        "sum": 100
    }
