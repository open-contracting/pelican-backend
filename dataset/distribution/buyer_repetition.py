"""
The most common buyer is identified in 1% to 50% of compiled releases.

Failure indicates issues in buyer identification or buyer over-representation. Buyers are identified by ``buyer.id``.

The test is skipped if the ``buyer.id`` field is present in fewer than 1,000 compiled releases.
"""

from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import deep_get

version = 2.0
min_items = 1000
sample_size = 20


def add_item(scope, item, item_id):
    if not scope:
        scope = {"buyers": {}, "total_ocid_count": 0}

    buyer_id = deep_get(item, "buyer.id")
    if buyer_id is None:
        return scope

    buyer_id = str(buyer_id)
    scope["buyers"].setdefault(buyer_id, ReservoirSampler(sample_size))
    scope["buyers"][buyer_id].process({"item_id": item_id, "ocid": item["ocid"]})
    scope["total_ocid_count"] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope or not scope["buyers"]:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    total_ocid_count = scope["total_ocid_count"]
    if total_ocid_count < min_items:
        result["meta"] = {"reason": f"fewer than {min_items} occurrences of necessary fields"}
        return result

    biggest_buyer_id = max(scope["buyers"], key=lambda key: scope["buyers"][key].index)
    biggest_buyer = scope["buyers"][biggest_buyer_id]
    biggest_buyer_share = biggest_buyer.index / total_ocid_count
    passed = 0.01 < biggest_buyer_share < 0.5

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "total_ocid_count": total_ocid_count,
        "ocid_count": biggest_buyer.index,
        "ocid_share": biggest_buyer_share,
        "examples": biggest_buyer.sample,
        "specifics": {"buyer.id": biggest_buyer_id},
    }

    return result
