"""
``planning.budget.amount`` isn't less than 50%, or more than 150%, of ``tender.value``.

Values are converted to USD if necessary.

The test is skipped if an amount is missing, zero or non-numeric, if a currency is missing or unknown, if the two
amounts aren't both positive or both negative, or if currency conversion is necessary and the release date is invalid,
before 1999, or in the future.
"""

import datetime

from pelican.util.checks import complete_result_resource_pass_fail, get_empty_result_resource
from pelican.util.currency_converter import convert
from pelican.util.getter import deep_get

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    planning_currency = deep_get(item, "planning.budget.amount.currency")
    tender_currency = deep_get(item, "tender.value.currency")
    if planning_currency is None or tender_currency is None:
        result["meta"] = {"reason": "a currency is missing"}
        return result

    planning_amount = deep_get(item, "planning.budget.amount.amount", float)
    tender_amount = deep_get(item, "tender.value.amount", float)
    if planning_amount is None or tender_amount is None:
        result["meta"] = {"reason": "an amount is missing or non-numeric"}
        return result

    date = deep_get(item, "date", datetime.date)

    if planning_currency != tender_currency:
        planning_amount = convert(planning_amount, planning_currency, "USD", date)
        tender_amount = convert(tender_amount, tender_currency, "USD", date)

    if planning_amount in {0, None} or tender_amount in {0, None}:
        result["meta"] = {"reason": "an amount is zero or unconvertable"}
        return result

    if (tender_amount > 0 and planning_amount < 0) or (tender_amount < 0 and planning_amount > 0):
        result["meta"] = {"reason": "the amounts have different signs"}
        return result

    return complete_result_resource_pass_fail(
        result,
        abs(tender_amount - planning_amount) / abs(tender_amount) <= 0.5,
        {
            "tender.value": item["tender"]["value"],
            "planning.budget.amount": item["planning"]["budget"]["amount"],
        },
    )
