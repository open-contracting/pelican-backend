from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import get_values

version = 1.0
min_items = 1000
sample_size = 20


def add_item(scope, item, item_id):
    if not scope:
        scope = {"buyers": {}, "total_ocid_count": 0}

    # filtering values containing required fields
    values = get_values(item, "buyer.identifier", value_only=True)
    if not values:
        return scope

    buyer_identifier = values[0]
    if (
        "scheme" not in buyer_identifier
        or "id" not in buyer_identifier
        or buyer_identifier["scheme"] is None
        or buyer_identifier["id"] is None
    ):
        return scope

    ocid = get_values(item, "ocid", value_only=True)[0]
    scope["total_ocid_count"] += 1
    key = (buyer_identifier["scheme"], buyer_identifier["id"])

    if key not in scope["buyers"]:
        scope["buyers"][key] = {"total_ocid_count": 1, "example": {"item_id": item_id, "ocid": ocid}}
    else:
        scope["buyers"][key]["total_ocid_count"] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope or not scope["buyers"]:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    if scope["total_ocid_count"] < min_items:
        result["meta"] = {"reason": f"fewer than {min_items} occurrences of necessary fields"}
        return result

    # initializing histogram
    ocid_histogram = {
        "1": {"total_ocid_count": 0, "total_buyer_count": 0},
        "2_20": {"total_ocid_count": 0, "total_buyer_count": 0},
        "21_50": {"total_ocid_count": 0, "total_buyer_count": 0},
        "51_100": {"total_ocid_count": 0, "total_buyer_count": 0},
        "100+": {"total_ocid_count": 0, "total_buyer_count": 0},
    }

    buyer_with_one_ocid_sampler = ReservoirSampler(sample_size)

    # filling in the histogram
    for value in scope["buyers"].values():
        if value["total_ocid_count"] == 1:
            ocid_histogram["1"]["total_ocid_count"] += value["total_ocid_count"]
            ocid_histogram["1"]["total_buyer_count"] += 1
            buyer_with_one_ocid_sampler.process(value["example"])

        elif 2 <= value["total_ocid_count"] <= 20:
            ocid_histogram["2_20"]["total_ocid_count"] += value["total_ocid_count"]
            ocid_histogram["2_20"]["total_buyer_count"] += 1

        elif 21 <= value["total_ocid_count"] <= 50:
            ocid_histogram["21_50"]["total_ocid_count"] += value["total_ocid_count"]
            ocid_histogram["21_50"]["total_buyer_count"] += 1

        elif 51 <= value["total_ocid_count"] <= 100:
            ocid_histogram["51_100"]["total_ocid_count"] += value["total_ocid_count"]
            ocid_histogram["51_100"]["total_buyer_count"] += 1

        else:
            ocid_histogram["100+"]["total_ocid_count"] += value["total_ocid_count"]
            ocid_histogram["100+"]["total_buyer_count"] += 1

    passed = ocid_histogram["1"]["total_buyer_count"] < 0.5 * len(scope["buyers"])

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "counts": ocid_histogram,
        "total_ocid_count": scope["total_ocid_count"],
        "total_buyer_count": len(scope["buyers"]),
        "examples": buyer_with_one_ocid_sampler.sample,
    }

    return result
