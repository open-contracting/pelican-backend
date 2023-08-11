"""
A random sample of 100 URL values return responses without HTTP error codes. The URL fields are:

-  ``planning.documents.url``
-  ``tender.documents.url``
-  ``awards.documents.url``
-  ``contracts.documents.url``
-  ``contracts.implementation.documents.url``
"""

import requests

from pelican.util import settings
from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import deep_get

version = 1.0
min_items = 100

paths = [
    "planning.documents.url",
    "tender.documents.url",
    "awards.documents.url",
    "contracts.documents.url",
    "contracts.implementation.documents.url",
]


def add_item(scope, item, item_id):
    scope.setdefault("samples", ReservoirSampler(min_items))

    ocid = item["ocid"]

    for path in paths:
        for value in deep_get(item, path, list):
            if type(value) is str:
                scope["samples"].process({"value": value, "item_id": item_id, "ocid": ocid})

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    sampler = scope["samples"]
    if not scope or not sampler:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    total_count = len(sampler)
    if total_count < min_items:
        result["meta"] = {"reason": f"fewer than {min_items} occurrences of necessary fields"}
        return result

    passed_count = 0
    passed_examples = []
    failed_examples = []
    for sample in sampler:
        try:
            response = requests.get(sample["value"], timeout=settings.REQUESTS_TIMEOUT, stream=True)
            if 200 <= response.status_code < 400:
                sample["status"] = "OK"
                passed_examples.append(sample)
                passed_count += 1
            else:
                sample["status"] = response.status_code
                failed_examples.append(sample)
        except requests.RequestException:
            sample["status"] = "ERROR"
            failed_examples.append(sample)

    result["result"] = passed_count == total_count
    result["value"] = 100 * passed_count / total_count
    result["meta"] = {
        "total_processed": total_count,
        "total_passed": passed_count,
        "total_failed": total_count - passed_count,
        "passed_examples": passed_examples,
        "failed_examples": failed_examples,
    }

    return result
