from contracting_process.resource_level.consistent.contracts_implementation_transactions_value import calculate
from tools.currency_converter import bootstrap

bootstrap()

item_empty = {"contracts": [{}, {"implementation": {}}, {"implementation": {"transactions": []}}]}
item_same_id = {
    "awards": [{"id": 1}, {"id": 1, "title": ""}],
    "contracts": [
        {"awardID": 0, "implementation": {"transactions": [{}]}},
        {"awardID": 1, "implementation": {"transactions": [{}]}},
    ],
}


def test_undefined():
    result = calculate({})
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "insufficient data for check"}

    result = calculate(item_empty)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "insufficient data for check"}

    result = calculate(item_same_id)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "insufficient data for check"}


item_test_passed1 = {
    "date": "2019-01-01T16:47:36.860000Z",
    "awards": [{"id": 0}],
    "contracts": [
        {
            "awardID": 0,
            "value": {"amount": 300, "currency": "CZK"},
            "implementation": {
                "transactions": [
                    {"value": {"amount": 100, "currency": "CZK"}},
                    {"value": {"amount": 100, "currency": "CZK"}},
                    {"value": {"amount": 100, "currency": "CZK"}},
                ]
            },
        }
    ],
}

item_test_passed2 = {
    "date": "2019-01-01T16:47:36.860000Z",
    "awards": [{"id": 1}],
    "contracts": [
        {
            "awardID": 0,
            "value": {"amount": 20, "currency": "GBP"},
            "implementation": {
                "transactions": [
                    {"value": {"amount": 100, "currency": "CZK"}},
                    {"value": {"amount": 100, "currency": "CZK"}},
                    {"value": {"amount": 100, "currency": "CZK"}},
                ]
            },
        }
    ],
}


def test_passed():
    result = calculate(item_test_passed1)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "contracts": [
            {"path": "contracts[0]", "contract_amount": 300, "transactions_amount_sum": 300, "currency": "CZK"}
        ]
    }

    result = calculate(item_test_passed2)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"]["contracts"][0]["path"] == "contracts[0]"
    assert result["meta"]["contracts"][0]["contract_amount"] > 0
    assert result["meta"]["contracts"][0]["transactions_amount_sum"] > 0
    assert result["meta"]["contracts"][0]["currency"] == "USD"


item_test_failed = {
    "date": "2019-01-01T16:47:36.860000Z",
    "awards": [{"id": 0}, {"id": 1}],
    "contracts": [
        {
            "awardID": 0,
            "value": {"amount": 300, "currency": "CZK"},
            "implementation": {
                "transactions": [
                    {"value": {"amount": 100, "currency": "CZK"}},
                    {"value": {"amount": 100, "currency": "CZK"}},
                    {"value": {"amount": 100, "currency": "CZK"}},
                ]
            },
        },
        {
            "awardID": 1,
            "value": {"amount": 300, "currency": "CZK"},
            "implementation": {"transactions": [{"value": {"amount": 301, "currency": "CZK"}}]},
        },
    ],
}


def test_failed():
    result = calculate(item_test_failed)
    assert result["result"] is False
    assert result["application_count"] == 2
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "contracts": [
            {"path": "contracts[0]", "contract_amount": 300, "transactions_amount_sum": 300, "currency": "CZK"},
            {"path": "contracts[1]", "contract_amount": 300, "transactions_amount_sum": 301, "currency": "CZK"},
        ]
    }
