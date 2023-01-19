import random

import requests

from pelican.util import settings
from pelican.util.checks import get_empty_result_dataset
from pelican.util.getter import get_values

version = 1.0
samples_num = 100

paths = [
    "planning.documents.url",
    "tender.documents.url",
    "awards.documents.url",
    "contracts.documents.url",
    "contracts.implementation.documents.url",
]


def add_item(scope, item, item_id):
    if "index" not in scope or "samples" not in scope:
        scope["index"] = 0
        scope["samples"] = []

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
        if scope["index"] < samples_num:
            scope["samples"].append(value)
        else:
            r = random.randint(0, scope["index"])
            if r < samples_num:
                scope["samples"][r] = value

        scope["index"] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    # not enough urls
    if len(scope["samples"]) < samples_num:
        result["meta"] = {"reason": f"there is less than {samples_num} URLs in the dataset"}
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
                sample["status"] = "ERROR"
        except requests.RequestException:
            sample["status"] = "ERROR"

    result["result"] = ok_status_num == samples_num
    result["value"] = 100 * (ok_status_num / samples_num)
    result["meta"] = {
        "total_processed": samples_num,
        "total_passed": ok_status_num,
        "total_failed": samples_num - ok_status_num,
        "passed_examples": [sample for sample in scope["samples"] if sample["status"] == "OK"],
        "failed_examples": [sample for sample in scope["samples"] if sample["status"] == "ERROR"],
    }

    return result
