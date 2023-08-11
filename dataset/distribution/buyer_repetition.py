"""
The most common buyer is identified in 1% to 50% of compiled releases. Failure indicates issues in buyer identification
or buyer over-representation. Buyers are identified by ``buyer.identifier.scheme`` and ``buyer.identifier.id``.

The test is skipped if the ``buyer.identifier.scheme`` and ``buyer.identifier.id`` fields are both present in fewer
than 1,000 compiled releases.
"""

from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import deep_get

version = 1.0
min_items = 1000
sample_size = 20


def add_item(scope, item, item_id):
    if not scope:
        scope = {"buyers": {}, "total_ocid_count": 0}

    scheme = deep_get(item, "buyer.identifier.scheme", str)
    ident = deep_get(item, "buyer.identifier.id", str)
    if not scheme or not ident:
        return scope

    identifier = (scheme, ident)
    scope["buyers"].setdefault(identifier, ReservoirSampler(sample_size))
    scope["buyers"][identifier].process({"item_id": item_id, "ocid": item["ocid"]})
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

    biggest_buyer_scheme, biggest_buyer_id = max(scope["buyers"], key=lambda key: scope["buyers"][key].index)
    biggest_buyer = scope["buyers"][(biggest_buyer_scheme, biggest_buyer_id)]
    biggest_buyer_share = biggest_buyer.index / total_ocid_count
    passed = 0.01 < biggest_buyer_share < 0.5

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "total_ocid_count": total_ocid_count,
        "ocid_count": biggest_buyer.index,
        "ocid_share": biggest_buyer_share,
        "examples": biggest_buyer.sample,
        "specifics": {"buyer.identifier.scheme": biggest_buyer_scheme, "buyer.identifier.id": biggest_buyer_id},
    }

    return result
