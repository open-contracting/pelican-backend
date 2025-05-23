import json
import os

from dataset.distribution import value_repetition

items_test_undefined_multiple = [
    {"ocid": "0"},
    {"ocid": "1", "contracts": [{"value": {"amount": 1, "currency": "USD"}}]},
]


def test_undefined():
    tender_value_repetition = value_repetition.ModuleType("tender")

    scope = {}
    for item_id, item in enumerate(items_test_undefined_multiple):
        scope = tender_value_repetition.add_item(scope, item, item_id)
    result = tender_value_repetition.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}


def get_currencies():
    with open(os.path.join("pelican", "static", "release-schema.json")) as f:
        schema = json.load(f)
        return schema["definitions"]["Value"]["properties"]["currency"]["enum"]


currencies = get_currencies()

item_test_passed1 = {
    "ocid": "1",
    "contracts": [{"value": {"amount": amount, "currency": "USD"}} for amount in range(100)],
}
item_test_passed2 = {
    "ocid": "1",
    "contracts": [{"value": {"amount": 0, "currency": currencies[i]}} for i in range(200)],
}


def test_passed():
    contracts_value_repetition = value_repetition.ModuleType("contracts")

    scope = {}
    scope = contracts_value_repetition.add_item(scope, item_test_passed1, 1)
    result = contracts_value_repetition.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100 * 3 * 0.01
    assert len(result["meta"]["most_frequent"]) == 5
    assert all(el["share"] == 0.01 for el in result["meta"]["most_frequent"])
    assert all(el["count"] == 1 for el in result["meta"]["most_frequent"])

    scope = {}
    scope = contracts_value_repetition.add_item(scope, item_test_passed2, 1)
    result = contracts_value_repetition.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100 * 3 * 0.005
    assert len(result["meta"]["most_frequent"]) == value_repetition.most_frequent_report_limit
    assert all(el["share"] == 0.005 for el in result["meta"]["most_frequent"])
    assert all(el["count"] == 1 for el in result["meta"]["most_frequent"])


items_test_failed = [
    {"ocid": str(ocid), "awards": [{"value": {"amount": 0, "currency": "USD"}}]} for ocid in range(100)
]
items_test_failed.extend(
    [{"ocid": str(i), "awards": [{"value": {"amount": i, "currency": "USD"}}]} for i in range(100, 1000)]
)


def test_failed():
    awards_value_repetition = value_repetition.ModuleType("awards")

    scope = {}
    for item_id, item in enumerate(items_test_failed):
        scope = awards_value_repetition.add_item(scope, item, item_id)
    result = awards_value_repetition.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 10.2
    assert len(result["meta"]["most_frequent"]) == 5
    assert result["meta"]["most_frequent"][0]["share"] == 0.1
    assert result["meta"]["most_frequent"][0]["count"] == 100
    assert result["meta"]["most_frequent"][0]["amount"] == 0
    assert result["meta"]["most_frequent"][0]["currency"] == "USD"
