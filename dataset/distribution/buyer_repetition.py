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

    scope["buyers"].setdefault(
        key,
        {
            "total_ocid_count": 0,
            "sampler": ReservoirSampler(sample_size),
        },
    )
    scope["buyers"][key]["total_ocid_count"] += 1
    scope["buyers"][key]["sampler"].process({"item_id": item_id, "ocid": ocid})

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope or not scope["buyers"]:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    if scope["total_ocid_count"] < min_items:
        result["meta"] = {"reason": f"fewer than {min_items} occurrences of necessary fields"}
        return result

    biggest_buyer_scheme, biggest_buyer_id = max(
        scope["buyers"], key=(lambda key: scope["buyers"][key]["total_ocid_count"])
    )
    biggest_buyer = scope["buyers"][(biggest_buyer_scheme, biggest_buyer_id)]

    passed = (0.01 * scope["total_ocid_count"]) < biggest_buyer["total_ocid_count"] < (0.5 * scope["total_ocid_count"])

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "total_ocid_count": scope["total_ocid_count"],
        "ocid_count": biggest_buyer["total_ocid_count"],
        "ocid_share": biggest_buyer["total_ocid_count"] / scope["total_ocid_count"],
        "examples": biggest_buyer["sampler"].sample,
        "specifics": {"buyer.identifier.id": biggest_buyer_id, "buyer.identifier.scheme": biggest_buyer_scheme},
    }

    return result
