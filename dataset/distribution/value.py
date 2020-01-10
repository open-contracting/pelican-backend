import operator
import functools

from tools.checks import get_empty_result_dataset
from tools.getter import get_values
from tools.helpers import parse_date
from tools.currency_converter import convert, currency_available


version = 1.0


class ModuleType:
    def __init__(self, path):
        self.add_item = functools.partial(add_item, path=path)
        self.get_result = get_result


def add_item(scope, item, item_id, path):
    if "values" not in scope:
        scope["values"] = []

    if type(item) == dict:
        ocid = get_values(item, "ocid", value_only=True)[0]
        values = get_values(item, path)
        if values:
            for value in values:
                value["item_id"] = item_id
                value["ocid"] = ocid

                if "currency" not in value["value"] or value["value"]["currency"] is None or \
                        "amount" not in value["value"] or value["value"]["amount"] is None or \
                        float(value["value"]["amount"]) < 0:
                    continue

                if currency_available(value["value"]["currency"]):
                    if value["value"]["currency"] != "USD":
                        if "date" in item and item["date"]:
                            rel_date = parse_date(item["date"])
                            value["abs_amount"] = convert(
                                value["value"]["amount"],
                                value["value"]["currency"],
                                "USD", rel_date)
                        if "abs_amount" in value and value["abs_amount"] is not None:
                            scope["values"].append(value)
                    else:
                        value["abs_amount"] = value["value"]["amount"]
                        scope["values"].append(value)

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if scope:
        values = scope["values"]
        count = len(values)
        if (count > 99):
            sum_value = sum(int(value["abs_amount"]) for value in values)

            percent_size = int(count/100)
            percent_index_1 = (percent_size)
            percent_index_5 = (5 * percent_size)
            percent_index_20 = (20 * percent_size)
            percent_index_50 = (50 * percent_size)

            sorted_values = sorted(values, key=lambda s: int(s["abs_amount"]), reverse=True)

            count_0_1_percent = len(sorted_values[:percent_index_1])
            count_1_5_percent = len(sorted_values[percent_index_1:percent_index_5])
            count_5_20_percent = len(sorted_values[percent_index_5:percent_index_20])
            count_20_50_percent = len(sorted_values[percent_index_20:percent_index_50])
            count_50_100_percent = len(sorted_values[percent_index_50:])

            sum_0_1_percent = sum(
                int(value["abs_amount"])
                for value in sorted_values[:percent_index_1]
            )
            sum_1_5_percent = sum(
                int(value["abs_amount"])
                for value in sorted_values[percent_index_1:percent_index_5]
            )
            sum_5_20_percent = sum(
                int(value["abs_amount"])
                for value in sorted_values[percent_index_5:percent_index_20]
            )
            sum_20_50_percent = sum(
                int(value["abs_amount"])
                for value in sorted_values[percent_index_20:percent_index_50]
            )
            sum_50_100_percent = sum(
                int(value["abs_amount"])
                for value in sorted_values[percent_index_50:]
            )

            result["meta"] = {
                "shares": {
                    "0_1": sum_0_1_percent / sum_value,
                    "1_5": sum_1_5_percent / sum_value,
                    "5_20": sum_5_20_percent / sum_value,
                    "20_50": sum_20_50_percent / sum_value,
                    "50_100": sum_50_100_percent / sum_value
                },
                "sums": {
                    "0_1": sum_0_1_percent,
                    "1_5": sum_1_5_percent,
                    "5_20": sum_5_20_percent,
                    "20_50": sum_20_50_percent,
                    "50_100": sum_50_100_percent
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
                "sum": sum_value
            }

            if sum_0_1_percent > (sum_value / 2):
                result["result"] = False
                result["value"] = 0
            else:
                result["result"] = True
                result["value"] = 100
            return result
        else:
            result["meta"] = {"reason": "unsufficient amount of values (at least 100 required)"}
            return result
    else:
        return result
