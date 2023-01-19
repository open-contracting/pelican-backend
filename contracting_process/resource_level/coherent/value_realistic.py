"""
Each monetary value is between -5 billion USD and +5 billion USD.

Since the test operates on all value objects, the test silently ignores any missing or non-numeric amounts and any
missing or unknown currencies. If currency conversion is necessary, but the release date is invalid, before 1999, or in
the future, the test silently ignores the value.
"""

import datetime

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.currency_converter import convert
from tools.getter import deep_get, get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    values = []
    for path in (
        "tender.value",
        "tender.minValue",
        "awards.value",
        "contracts.value",
        "planning.budget.amount",
        "contracts.implementation.transactions.value",
    ):
        values.extend(get_values(item, path))

    application_count = 0
    pass_count = 0
    failed_paths = []
    for value in values:
        amount = deep_get(value["value"], "amount", float)

        if amount is None:  # non-numeric
            continue

        currency = deep_get(value["value"], "currency")

        if currency == "USD":
            usd_amount = amount
        else:
            date = deep_get(item, "date", datetime.date)
            if date is None:
                continue
            usd_amount = convert(amount, currency, "USD", date)
            if usd_amount is None:  # unconvertable
                continue

        passed = -5.0e9 <= float(usd_amount) <= 5.0e9

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append({"path": value["path"], "amount": amount, "currency": currency})

    return complete_result_resource(
        result,
        application_count,
        pass_count,
        reason="no numeric, convertable amounts",
        meta={"failed_paths": failed_paths},
    )
