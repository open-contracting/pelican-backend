from tools.getter import get_values
from tools.checks import get_empty_result_resource
from tools.helpers import parse_datetime
from tools.currency_converter import convert
from datetime import date
from decimal import Decimal

version = 1.0

"""
author: Iaroslav Kolodka

version 1.0

"""


def calculate(item):
    """
    The function controls 'Value' object for a realistic value in it.

    Parameters
    ----------
    version : item
        tested JSON

    Returns
    -------
    dict
        tests results

    """
    result = get_empty_result_resource(version)

    values = get_values(item, 'date', value_only=True)
    date = parse_datetime(values[0]) if values else None

    value_boxes = get_values(item, "tender.value")
    value_boxes += get_values(item, "tender.minValue")
    value_boxes += get_values(item, "awards.value")
    value_boxes += get_values(item, "contracts.value")
    value_boxes += get_values(item, "planning.budget.value")
    value_boxes += get_values(item, "contracts.implementation.transactions.value")

    application_count = 0
    pass_count = 0
    if value_boxes:
        lower_bound = Decimal(-5000000000)
        upper_bound = Decimal(5000000000)
        for value_box in value_boxes:
            passed = None
            value = None
            if "value" in value_box and value_box["value"]:
                value_amount = get_values(value_box["value"], "amount", True)
                if not value_amount:  # check on empty list
                    continue
                value_amount = value_amount[0]
                if value_amount is None:
                    continue
                try:
                    value_amount_int = int(float(value_amount))
                    value_currency = get_values(value_box["value"], "currency", True)
                    if not value_currency:
                        continue
                    value_currency = value_currency[0]
                    if value_currency is not "USD":
                        value_amount_usd = convert(amount=value_amount_int,
                                                   original_currency=value_currency,
                                                   target_currency="USD",
                                                   rel_date=date)
                    else:
                        value_amount_usd = value_amount_int
                    if value_amount_usd is None:
                        continue
                    application_count += 1

                    passed = value_amount_usd >= lower_bound and value_amount_usd <= upper_bound
                    pass_count = pass_count + 1 if passed else pass_count
                    if not result["meta"]:
                        result["meta"] = {"references": []}
                    result["meta"]["references"].append(
                        {
                            "result": passed,
                            "amount": value_amount,
                            "currency": value_currency,
                            "path": value_box["path"]
                        }
                    )
                except ValueError:
                    continue
        if application_count > 0:  # else: None
            result["result"] = application_count == pass_count

    result["application_count"] = application_count
    result["pass_count"] = pass_count
    return result
