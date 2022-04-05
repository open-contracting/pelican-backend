import functools
import random

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
examples_cap = 10
most_frequent_cap = 5
most_frequent_computation = 3


class ModuleType:
    def __init__(self, path):
        self.add_item = functools.partial(add_item, path=path)
        self.get_result = get_result


def add_item(scope, item, item_id, path):
    if scope is None:
        scope = {}

    ocid = get_values(item, "ocid", value_only=True)[0]

    values = get_values(item, f"{path}.value", value_only=True)
    if not values:
        return scope

    # check whether amount and currency fields are set
    values = [
        v
        for v in values
        if ("amount" in v and "currency" in v and v["amount"] is not None and v["currency"] is not None)
    ]

    # intermediate computation
    for value in values:
        key = (value["amount"], value["currency"])
        if key not in scope:
            scope[key] = {
                "amount": value["amount"],
                "currency": value["currency"],
                "value_str": f"{value['amount']} {value['currency']}",
                "count": 0,
                "examples": [],
            }

        # reservoir sampling
        if scope[key]["count"] < examples_cap:
            scope[key]["examples"].append({"item_id": item_id, "ocid": ocid})
        else:
            r = random.randint(0, scope[key]["count"])
            if r < examples_cap:
                scope[key]["examples"][r] = {"item_id": item_id, "ocid": ocid}

        scope[key]["count"] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if scope:
        total_count = 0
        most_frequent = []

        # determine three most frequent value.amount and value.currency combinations
        for key in scope:
            most_frequent.append(key)
            most_frequent.sort(key=lambda k: scope[k]["count"], reverse=True)
            most_frequent = most_frequent[:most_frequent_cap]

            total_count += scope[key]["count"]

        most_frequent_count = sum([scope[k]["count"] for k in most_frequent[:most_frequent_computation]])

        most_frequent_share = most_frequent_count / total_count
        passed = most_frequent_share < 0.1

        for key in most_frequent:
            scope[key]["share"] = scope[key]["count"] / total_count

        result["result"] = passed
        result["value"] = 100 * most_frequent_share
        result["meta"] = {"most_frequent": [scope[key] for key in most_frequent], "total_processed": total_count}
    else:
        result["meta"] = {"reason": "there are is no suitable data item for this check"}

    return result
