"""
The 3 most frequent ``amount`` and ``currency`` pairs appear in fewer than 10% of cases.

The test is skipped if there are no pairs.
"""

import functools
import heapq

from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import deep_get, get_values

version = 1.0
sample_size = 10
most_frequent_report_limit = 5
most_frequent_test_limit = 3


class ModuleType:
    def __init__(self, path):
        self.add_item = functools.partial(add_item, path=path)
        self.get_result = get_result


def add_item(scope, item, item_id, path):
    ocid = item["ocid"]

    # Use get_values(), since `path` can contain an array as an ancestor.
    for value in get_values(item, f"{path}.value", value_only=True):
        currency = deep_get(value, "currency")
        if currency is None:
            continue

        amount = deep_get(value, "amount")
        if amount is None:
            continue

        key = (amount, currency)
        # Note: The scope is returned in meta, so any changes can affect pelican-frontend.
        scope.setdefault(
            key,
            {
                "amount": amount,
                "currency": currency,
                "value_str": f"{amount} {currency}",
                "examples": ReservoirSampler(sample_size),
            },
        )

        scope[key]["examples"].process({"item_id": item_id, "ocid": ocid})

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
        item = (value["examples"].index, -i, key)
        if len(most_frequent) < most_frequent_report_limit:
            heapq.heappush(most_frequent, item)
        else:
            heapq.heappushpop(most_frequent, item)
        total_count += value["examples"].index

    most_frequent = [(key, count) for count, _, key in sorted(most_frequent, reverse=True)]
    most_frequent_count = sum(count for _, count in most_frequent[:most_frequent_test_limit])
    most_frequent_share = most_frequent_count / total_count
    passed = most_frequent_share < 0.1

    for key, count in most_frequent:
        scope[key]["share"] = count / total_count
        scope[key]["count"] = scope[key]["examples"].index
        scope[key]["examples"] = scope[key].pop("examples").sample  # re-order to end

    result["result"] = passed
    result["value"] = 100 * most_frequent_share
    result["meta"] = {"most_frequent": [scope[key] for key, _ in most_frequent], "total_processed": total_count}

    return result
