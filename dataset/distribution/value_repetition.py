"""
The 3 most frequent ``amount`` and ``currency`` pairs appear in fewer than 10% of cases.
"""

import functools
import heapq
import random

from pelican.util.checks import get_empty_result_dataset
from pelican.util.getter import get_values

version = 1.0
sample_size = 10
most_frequent_cap = 5
most_frequent_computation = 3


class ModuleType:
    def __init__(self, path):
        self.add_item = functools.partial(add_item, path=path)
        self.get_result = get_result


def add_item(scope, item, item_id, path):
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
        if scope[key]["count"] < sample_size:
            scope[key]["examples"].append({"item_id": item_id, "ocid": ocid})
        else:
            r = random.randint(0, scope[key]["count"])
            if r < sample_size:
                scope[key]["examples"][r] = {"item_id": item_id, "ocid": ocid}

        scope[key]["count"] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    total_count = 0
    most_frequent = []

    # Use `i` as tie-breaker.
    for i, (key, value) in enumerate(scope.items()):
        item = (value["count"], -i, key)
        if len(most_frequent) < most_frequent_cap:
            heapq.heappush(most_frequent, item)
        else:
            heapq.heappushpop(most_frequent, item)
        total_count += value["count"]

    most_frequent = [(key, count) for count, _, key in sorted(most_frequent, reverse=True)]

    most_frequent_count = sum(count for _, count in most_frequent[:most_frequent_computation])

    most_frequent_share = most_frequent_count / total_count
    passed = most_frequent_share < 0.1

    for key, count in most_frequent:
        scope[key]["share"] = count / total_count

    result["result"] = passed
    result["value"] = 100 * most_frequent_share
    result["meta"] = {"most_frequent": [scope[key] for key, _ in most_frequent], "total_processed": total_count}

    return result
