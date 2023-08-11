"""
The total value of the top 1% of values is less than the total value of the remaining values. Failure indicates extreme
outliers in the top 1%. All values are converted to USD as of the compiled release's ``date``.

The test is skipped if fewer than 100 values are included. A value is excluded if an amount is missing, negative or
non-numeric, if a currency is missing or unknown, or if currency conversion is necessary and the release date is
invalid, before 1999, or in the future.
"""

import datetime
import functools

from pelican.util.checks import get_empty_result_dataset
from pelican.util.getter import deep_get, get_amount, get_values

version = 1.0
min_items = 100  # "top 1%" must match at least 1 value
sample_size = 10


class ModuleType:
    def __init__(self, path):
        self.add_item = functools.partial(add_item, path=path)
        self.get_result = get_result


def add_item(scope, item, item_id, path):
    scope.setdefault("values", [])

    ocid = item["ocid"]
    date = deep_get(item, "date", datetime.date)

    # Use get_values(), since `path` can contain an array as an ancestor.
    for value in get_values(item, path):
        currency = deep_get(value["value"], "currency")
        if currency is None:
            continue

        amount = deep_get(value["value"], "amount", float)
        if amount is None or amount < 0:  # negative numbers confuse sums
            continue

        usd_amount = get_amount(currency == "USD", amount, currency, date)
        if usd_amount is None:
            continue

        value["item_id"] = item_id
        value["ocid"] = ocid
        value["abs_amount"] = int(usd_amount)
        scope["values"].append(value)

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope or not scope["values"]:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    values = scope["values"]
    count = len(values)
    if count < min_items:
        result["meta"] = {"reason": f"fewer than {min_items} occurrences of necessary fields"}
        return result

    sum_value = sum(value["abs_amount"] for value in values)
    if sum_value == 0:
        result["meta"] = {"reason": "sum is 0, causing division by zero error"}
        return result

    sorted_values = sorted(values, key=lambda item: item["abs_amount"], reverse=True)
    percent_size = int(count / 100)
    percent_index_1 = percent_size
    percent_index_5 = 5 * percent_size
    percent_index_20 = 20 * percent_size
    percent_index_50 = 50 * percent_size
    sum_0_1_percent = sum(value["abs_amount"] for value in sorted_values[:percent_index_1])
    sum_1_5_percent = sum(value["abs_amount"] for value in sorted_values[percent_index_1:percent_index_5])
    sum_5_20_percent = sum(value["abs_amount"] for value in sorted_values[percent_index_5:percent_index_20])
    sum_20_50_percent = sum(value["abs_amount"] for value in sorted_values[percent_index_20:percent_index_50])
    sum_50_100_percent = sum(value["abs_amount"] for value in sorted_values[percent_index_50:])
    passed = sum_0_1_percent <= (sum_value / 2)

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "shares": {
            "0_1": sum_0_1_percent / sum_value,
            "1_5": sum_1_5_percent / sum_value,
            "5_20": sum_5_20_percent / sum_value,
            "20_50": sum_20_50_percent / sum_value,
            "50_100": sum_50_100_percent / sum_value,
        },
        "sums": {
            "0_1": sum_0_1_percent,
            "1_5": sum_1_5_percent,
            "5_20": sum_5_20_percent,
            "20_50": sum_20_50_percent,
            "50_100": sum_50_100_percent,
        },
        "counts": {
            "0_1": len(sorted_values[:percent_index_1]),
            "1_5": len(sorted_values[percent_index_1:percent_index_5]),
            "5_20": len(sorted_values[percent_index_5:percent_index_20]),
            "20_50": len(sorted_values[percent_index_20:percent_index_50]),
            "50_100": len(sorted_values[percent_index_50:]),
        },
        "examples": {
            "0_1": sorted_values[:percent_index_1][:sample_size],
            "1_5": sorted_values[percent_index_1:percent_index_5][:sample_size],
            "5_20": sorted_values[percent_index_5:percent_index_20][:sample_size],
            "20_50": sorted_values[percent_index_20:percent_index_50][:sample_size],
            "50_100": sorted_values[percent_index_50:][:sample_size],
        },
        "sum": sum_value,
    }

    return result
