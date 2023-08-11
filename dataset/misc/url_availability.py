import random

import requests

from pelican.util import settings
from pelican.util.checks import get_empty_result_dataset
from pelican.util.getter import get_values

version = 1.0
sample_size = 100

paths = [
    "planning.documents.url",
    "tender.documents.url",
    "awards.documents.url",
    "contracts.documents.url",
    "contracts.implementation.documents.url",
]


def add_item(scope, item, item_id):
    if not scope:
        scope = {"samples": [], "index": 0}  # index is only used within this function

    ocid = get_values(item, "ocid", value_only=True)[0]

    values = []
    for path in paths:
        pos_values = get_values(item, path)
        if not pos_values:
            continue

        for value in pos_values:
            value["item_id"] = item_id
            value["ocid"] = ocid
            if value["value"] is not None:
                values.append(value)

    # reservoir sampling
    for value in values:
        if scope["index"] < sample_size:
            scope["samples"].append(value)
        else:
            r = random.randint(0, scope["index"])
            if r < sample_size:
                scope["samples"][r] = value

        scope["index"] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope or not scope["samples"]:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    if len(scope["samples"]) < sample_size:
        result["meta"] = {"reason": f"fewer than {sample_size} occurrences of necessary fields"}
        return result

    # checking url status
    ok_status_num = 0
    for sample in scope["samples"]:
        try:
            response = requests.get(sample["value"], timeout=settings.REQUESTS_TIMEOUT, stream=True)
            if 200 <= response.status_code < 400:
                sample["status"] = "OK"
                ok_status_num += 1
            else:
                sample["status"] = response.status_code
        except requests.RequestException:
            sample["status"] = "ERROR"

    result["result"] = ok_status_num == sample_size
    result["value"] = 100 * (ok_status_num / sample_size)
    result["meta"] = {
        "total_processed": sample_size,
        "total_passed": ok_status_num,
        "total_failed": sample_size - ok_status_num,
        "passed_examples": [sample for sample in scope["samples"] if sample["status"] == "OK"],
        "failed_examples": [sample for sample in scope["samples"] if sample["status"] != "OK"],
    }

    return result
