import operator
from datetime import date, datetime

from currency_converter import CurrencyConverter

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0

c = CurrencyConverter("http://www.ecb.int/stats/eurofxref/eurofxref-hist.zip", fallback_on_wrong_date=True)


def add_item(scope, item, item_id):
    if "values" not in scope:
        scope["values"] = []

    if type(item) == dict:
        values = get_values(item, "contracts.value")
        if values:
            for value in values:
                value["item_id"] = item_id
                if value["value"]["currency"] in c.currencies:
                    if value["value"]["currency"] != "USD":
                        if item["date"]:
                            rel_date = datetime.strptime(item["date"][:9], "%Y-%m-%d").date()
                            value["abs_amount"] = int(c.convert(
                                value["value"]["amount"],
                                value["value"]["currency"],
                                'USD', rel_date))
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

            sum_0_1_percent = sum(int(value["abs_amount"]) for value in sorted_values[:percent_index_1])
            sum_1_5_percent = sum(int(value["abs_amount"])
                                  for value in sorted_values[percent_index_1:percent_index_5])
            sum_5_20_percent = sum(int(value["abs_amount"])
                                   for value in sorted_values[percent_index_5:percent_index_20])
            sum_20_50_percent = sum(int(value["abs_amount"])
                                    for value in sorted_values[percent_index_20:percent_index_50])
            sum_50_100_percent = sum(int(value["abs_amount"]) for value in sorted_values[percent_index_50:])

            result["meta"] = {
                "shares": {
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
            result["meta"] = {"reason": "unsufficient amount of contract values (at least 100 required)"}
            return result
    else:
        return result
