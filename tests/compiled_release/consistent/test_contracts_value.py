from contracting_process.resource_level.consistent.contracts_value import calculate
from tools.bootstrap import bootstrap

bootstrap("contracts_value_test")


item_no_contracts = {"date": "2019-01-10T22:00:00+01:00", "contracts": []}
item_no_awards = {"date": "2019-01-10T22:00:00+01:00", "contracts": [{"awardID": 0}], "awards": []}
item_same_id = {
    "date": "2019-01-10T22:00:00+01:00",
    "contracts": [{"awardID": 0}],
    "awards": [{"id": 0}, {"id": 0, "title": ""}],
}
item_missing_fields = {
    "date": "2019-01-10T22:00:00+01:00",
    "contracts": [{"awardID": 0}],
    "awards": [{"id": 0}],
}
item_no_rate = {
    "date": "2019-01-10T22:00:00+01:00",
    "contracts": [{"awardID": 0, "value": {"currency": "UYW", "amount": 100}}],
    "awards": [{"id": 0, "value": {"currency": "USD", "amount": 100}}],
}


def test_undefined():
    result = calculate(item_no_contracts)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "there are no contracts"}

    result = calculate(item_no_awards)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "there are no awards"}

    result = calculate(item_no_rate)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "rule could not be applied for any award - contracts group"}

    result = calculate(item_same_id)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "rule could not be applied for any award - contracts group"}

    result = calculate(item_missing_fields)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "rule could not be applied for any award - contracts group"}


item_test_passed1 = {
    "contracts": [
        {"awardID": "str", "value": {"currency": "USD", "amount": 100}},
        {"awardID": "str", "value": {"currency": "USD", "amount": 25}},
    ],
    "awards": [{"id": "str", "value": {"currency": "USD", "amount": 100}}],
}

item_test_passed2 = {
    "contracts": [
        {"awardID": "str1", "value": {"currency": "USD", "amount": 100}},
        {"awardID": "str1", "value": {"currency": "USD", "amount": 25}},
        {"awardID": "unknown", "value": {"currency": "USD", "amount": 25}},
        {"awardID": "str2", "value": {"currency": "USD", "amount": 25}},
        {
            "awardID": "str2",
            "value": {
                "currency": "USD",
            },
        },
    ],
    "awards": [
        {"id": "str1", "value": {"currency": "USD", "amount": 100}},
        {"id": "str2", "value": {"currency": "USD", "amount": 100}},
    ],
}


def test_passed():
    result = calculate(item_test_passed1)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "awards": [{"awardID": "str", "awards.value": {"amount": 100, "currency": "USD"}, "contracts.value_sum": 125}]
    }

    result = calculate(item_test_passed2)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "awards": [{"awardID": "str1", "awards.value": {"amount": 100, "currency": "USD"}, "contracts.value_sum": 125}]
    }


item_test_failed = {
    "contracts": [
        {"awardID": "str", "value": {"currency": "USD", "amount": -100}},
        {"awardID": "str", "value": {"currency": "USD", "amount": -51}},
    ],
    "awards": [{"id": "str", "value": {"currency": "USD", "amount": -100}}],
}


def test_failed():
    result = calculate(item_test_failed)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "awards": [
            {"awardID": "str", "awards.value": {"amount": -100, "currency": "USD"}, "contracts.value_sum": -151}
        ]
    }


item_test_passed_multiple_awards = {
    "contracts": [
        {"awardID": 0, "value": {"currency": "USD", "amount": 100}},
        {"awardID": 0, "value": {"currency": "USD", "amount": 25}},
        {"awardID": 1, "value": {"currency": "USD", "amount": 10}},
    ],
    "awards": [
        {"id": 0, "value": {"currency": "USD", "amount": 100}},
        {"id": 1, "value": {"currency": "USD", "amount": 10}},
    ],
}


def test_passed_multiple_awards():
    result = calculate(item_test_passed_multiple_awards)
    assert result["result"] is True
    assert result["application_count"] == 2
    assert result["pass_count"] == 2
    assert result["meta"] == {
        "awards": [
            {"awardID": 0, "awards.value": {"amount": 100, "currency": "USD"}, "contracts.value_sum": 125},
            {"awardID": 1, "awards.value": {"amount": 10, "currency": "USD"}, "contracts.value_sum": 10},
        ]
    }


item_test_failed_multiple_awards = {
    "contracts": [
        {"awardID": 0, "value": {"currency": "USD", "amount": 100}},
        {"awardID": 0, "value": {"currency": "USD", "amount": 25}},
        {"awardID": 1, "value": {"currency": "USD", "amount": 1}},
    ],
    "awards": [
        {"id": 0, "value": {"currency": "USD", "amount": 100}},
        {"id": 1, "value": {"currency": "USD", "amount": 20}},
    ],
}


def test_failed_multiple_awards():
    result = calculate(item_test_failed_multiple_awards)
    assert result["result"] is False
    assert result["application_count"] == 2
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "awards": [
            {"awardID": 0, "awards.value": {"amount": 100, "currency": "USD"}, "contracts.value_sum": 125},
            {"awardID": 1, "awards.value": {"amount": 20, "currency": "USD"}, "contracts.value_sum": 1},
        ]
    }
