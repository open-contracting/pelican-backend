from tools.getter import get_values
from tools.checks import get_empty_result_resource
from currency_converter import CurrencyConverter
from datetime import date

version = 1.0

"""
author: Iaroslav Kolodka

version 1.0

"""


def value_realistic(item):
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

    value_boxes = get_values(item, "tender.value")
    value_boxes += get_values(item, "tender.minValue")
    value_boxes += get_values(item, "awards.value")
    value_boxes += get_values(item, "contracts.value")
    value_boxes += get_values(item, "planning.budget.value")
    value_boxes += get_values(item, "contracts.implementation.transactions.value")

    application_count = 0
    pass_count = 0
    if value_boxes:
        converter = CurrencyConverter()
        for value_box in value_boxes:
            passed = None
            value = None
            if "value" in value_box and value_box["value"]:
                value_amount = get_values(value_box["value"], "amount", True)
                if not value_amount:
                    continue
                value_amount = value_amount[0]
                try:
                    value_amount_int = int(float(value_amount))
                    value_currency = get_values(value_box["value"], "currency", True)
                    if not value_currency:
                        continue
                    value_currency = value_currency[0]
                    if value_currency is not "USD":
                        value_amount_usd = converter.convert(amount=value_amount_int,
                                                             currency=value_currency,
                                                             new_currency="USD")
                    else:
                        value_amount_usd = value_amount_int
                    application_count += 1
                    passed = value_amount_usd >= -1000000000 and value_amount_usd <= 1000000000
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
