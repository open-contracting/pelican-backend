from contracting_process.resource_level.coherent.value_realistic import calculate
from tools.bootstrap import bootstrap

version = 1.0
bootstrap("test", "value_realistic_test")

item_undefined1 = {"tender": {}, "date": "2019-01-10T22:00:00+01:00"}

item_undefined2 = {"tender": {"value": {}}, "date": "2019-01-10T22:00:00+01:00"}

item_undefined3 = {"tender": {"value": {"amount": None, "currency": "USD"}}, "date": "2019-01-10T22:00:00+01:00"}

item_undefined4 = {"tender": {"value": {"amount": 100, "currency": "unknown"}}, "date": "2019-01-10T22:00:00+01:00"}


def test_undefined():
    empty_result = calculate({"date": "2019-01-10T22:00:00+01:00"})
    assert empty_result["result"] is None
    assert empty_result["application_count"] == 0
    assert empty_result["pass_count"] == 0
    assert empty_result["meta"] == {"reason": "rule could not be applied for any value"}

    result = calculate(item_undefined1)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "rule could not be applied for any value"}

    result = calculate(item_undefined2)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "rule could not be applied for any value"}

    result = calculate(item_undefined3)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "rule could not be applied for any value"}

    result = calculate(item_undefined4)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "rule could not be applied for any value"}


item_passed = {
    "tender": {"value": {"amount": -5.0e9, "currency": "USD"}, "minValue": {"amount": 5.0e9, "currency": "USD"}},
    "awards": [
        {
            "value": {"amount": 0, "currency": "USD"},
        },
        {
            "value": {
                "amount": 100,
            },
        },
    ],
    "date": "2019-01-10T22:00:00+01:00",
}


def test_passed():
    result = calculate(item_passed)
    assert result["result"] is True
    assert result["application_count"] == 3
    assert result["pass_count"] == 3
    assert result["meta"] == {
        "references": [
            {"result": True, "amount": -5.0e9, "currency": "USD", "path": "tender.value"},
            {"result": True, "amount": 5.0e9, "currency": "USD", "path": "tender.minValue"},
            {"result": True, "amount": 0, "currency": "USD", "path": "awards[0].value"},
        ]
    }


item_failed = {
    "contracts": [{"value": {"amount": 500, "currency": "CZK"}}, {"value": {"amount": 5.0e10, "currency": "USD"}}],
    "planning": {"budget": {"value": {"amount": 0, "currency": "unknown"}}},
    "date": "2019-01-10T22:00:00+01:00",
}


def test_failed():
    result = calculate(item_failed)
    assert result["result"] is False
    assert result["application_count"] == 2
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "references": [
            {"result": True, "amount": 500, "currency": "CZK", "path": "contracts[0].value"},
            {"result": False, "amount": 5.0e10, "currency": "USD", "path": "contracts[1].value"},
        ]
    }
