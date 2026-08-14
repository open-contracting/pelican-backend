"""
Fewer than 50% of all buyers are identified in only one compiled release.

Failure indicates issues in buyer identification. Buyers are identified by ``buyer.id``.

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
    if buyer_id not in scope["buyers"]:
        scope["buyers"][buyer_id] = {"count": 1, "example": {"item_id": item_id, "ocid": item["ocid"]}}
    else:
        scope["buyers"][buyer_id]["count"] += 1
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

    ocid_histogram = {
        "1": {"total_ocid_count": 0, "total_buyer_count": 0},
        "2_20": {"total_ocid_count": 0, "total_buyer_count": 0},
        "21_50": {"total_ocid_count": 0, "total_buyer_count": 0},
        "51_100": {"total_ocid_count": 0, "total_buyer_count": 0},
        "100+": {"total_ocid_count": 0, "total_buyer_count": 0},
    }
    total_buyer_count = len(scope["buyers"])
    sampler = ReservoirSampler(sample_size)

    for value in scope["buyers"].values():
        if value["count"] == 1:
            ocid_histogram["1"]["total_ocid_count"] += value["count"]
            ocid_histogram["1"]["total_buyer_count"] += 1
            sampler.process(value["example"])
        elif 2 <= value["count"] <= 20:
            ocid_histogram["2_20"]["total_ocid_count"] += value["count"]
            ocid_histogram["2_20"]["total_buyer_count"] += 1
        elif 21 <= value["count"] <= 50:
            ocid_histogram["21_50"]["total_ocid_count"] += value["count"]
            ocid_histogram["21_50"]["total_buyer_count"] += 1
        elif 51 <= value["count"] <= 100:
            ocid_histogram["51_100"]["total_ocid_count"] += value["count"]
            ocid_histogram["51_100"]["total_buyer_count"] += 1
        else:
            ocid_histogram["100+"]["total_ocid_count"] += value["count"]
            ocid_histogram["100+"]["total_buyer_count"] += 1

    passed = ocid_histogram["1"]["total_buyer_count"] < 0.5 * total_buyer_count

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "counts": ocid_histogram,
        "total_ocid_count": total_ocid_count,
        "total_buyer_count": total_buyer_count,
        "examples": sampler.sample,
    }

    return result
