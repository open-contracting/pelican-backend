from tools.checks import complete_result_resource, get_empty_result_resource
from tools.currency_converter import convert
from tools.getter import get_values, parse_datetime

version = 1.0

value_paths = [
    "tender.value",
    "tender.minValue",
    "awards.value",
    "contracts.value",
    "planning.budget.amount",
    "contracts.implementation.transactions.value",
]


def calculate(item):
    result = get_empty_result_resource(version)

    value_fields = []
    for path in value_paths:
        value_fields.extend(get_values(item, path))

    application_count = 0
    pass_count = 0
    for value_field in value_fields:
        if "amount" not in value_field["value"] or "currency" not in value_field["value"]:
            continue

        if value_field["value"]["amount"] is None or value_field["value"]["currency"] is None:
            continue

        usd_amount = None
        if value_field["value"]["currency"] == "USD":
            usd_amount = value_field["value"]["amount"]
        else:
            if "date" not in item:
                continue

            usd_amount = convert(
                value_field["value"]["amount"], value_field["value"]["currency"], "USD", parse_datetime(item["date"])
            )

        if usd_amount is None:
            continue

        passed = -5.0e9 <= float(usd_amount) <= 5.0e9

        application_count += 1
        if passed:
            pass_count += 1

        if result["meta"] is None:
            result["meta"] = {"references": []}

        result["meta"]["references"].append(
            {
                "result": passed,
                "amount": value_field["value"]["amount"],
                "currency": value_field["value"]["currency"],
                "path": value_field["path"],
            }
        )

    return complete_result_resource(result, application_count, pass_count, reason="insufficient data for check")
