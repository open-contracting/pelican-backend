import datetime
import functools

from pelican.util.checks import get_empty_result_dataset
from pelican.util.getter import deep_get, get_amount, get_values

version = 1.0
min_items = 100


class ModuleType:
    def __init__(self, path):
        self.add_item = functools.partial(add_item, path=path)
        self.get_result = get_result


def add_item(scope, item, item_id, path):
    scope.setdefault("values", [])

    ocid = get_values(item, "ocid", value_only=True)[0]
    date = deep_get(item, "date", datetime.date)
    values = get_values(item, path)
    for value in values:
        currency = deep_get(value["value"], "currency")
        if currency is None:
            continue

        amount = deep_get(value["value"], "amount", float)
        if amount is None or amount < 0:
            continue

        usd_amount = get_amount(currency == "USD", amount, currency, date)
        if usd_amount is not None:
            value["item_id"] = item_id
            value["ocid"] = ocid
            value["abs_amount"] = usd_amount
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

    sum_value = sum(int(value["abs_amount"]) for value in values)
    if sum_value == 0:
        result["meta"] = {"reason": "sum is 0, causing division by zero error"}
        return result

    percent_size = int(count / 100)
    percent_index_1 = percent_size
    percent_index_5 = 5 * percent_size
    percent_index_20 = 20 * percent_size
    percent_index_50 = 50 * percent_size

    sorted_values = sorted(values, key=lambda item: int(item["abs_amount"]), reverse=True)

    count_0_1_percent = len(sorted_values[:percent_index_1])
    count_1_5_percent = len(sorted_values[percent_index_1:percent_index_5])
    count_5_20_percent = len(sorted_values[percent_index_5:percent_index_20])
    count_20_50_percent = len(sorted_values[percent_index_20:percent_index_50])
    count_50_100_percent = len(sorted_values[percent_index_50:])

    sum_0_1_percent = sum(int(value["abs_amount"]) for value in sorted_values[:percent_index_1])
    sum_1_5_percent = sum(int(value["abs_amount"]) for value in sorted_values[percent_index_1:percent_index_5])
    sum_5_20_percent = sum(int(value["abs_amount"]) for value in sorted_values[percent_index_5:percent_index_20])
    sum_20_50_percent = sum(int(value["abs_amount"]) for value in sorted_values[percent_index_20:percent_index_50])
    sum_50_100_percent = sum(int(value["abs_amount"]) for value in sorted_values[percent_index_50:])

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
            "0_1": count_0_1_percent,
            "1_5": count_1_5_percent,
            "5_20": count_5_20_percent,
            "20_50": count_20_50_percent,
            "50_100": count_50_100_percent,
        },
        "examples": {
            "0_1": sorted_values[:percent_index_1][:10],
            "1_5": sorted_values[percent_index_1:percent_index_5][:10],
            "5_20": sorted_values[percent_index_5:percent_index_20][:10],
            "20_50": sorted_values[percent_index_20:percent_index_50][:10],
            "50_100": sorted_values[percent_index_50:][:10],
        },
        "sum": sum_value,
    }

    passed = sum_0_1_percent <= (sum_value / 2)

    result["result"] = passed
    result["value"] = 100 if passed else 0

    return result
