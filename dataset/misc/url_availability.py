"""
A random sample of 100 URL values return responses without HTTP error codes.

The URL fields are:

-  ``planning.documents.url``
-  ``tender.documents.url``
-  ``awards.documents.url``
-  ``contracts.documents.url``
-  ``contracts.implementation.documents.url``

The test is skipped if fewer than 100 URL values are present.

Each unique URL is requested at most once.
"""

import requests

from pelican.util import settings
from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import get_values

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
    scope.setdefault("sampler", ReservoirSampler(min_items))

    ocid = item["ocid"]

    for path in paths:
        # Use get_values(), since `path` can contain an array as an ancestor.
        for value in get_values(item, path, value_only=True):
            if type(value) is str:
                scope["sampler"].process({"value": value, "item_id": item_id, "ocid": ocid})

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    sampler = scope["sampler"]
    if not scope or not sampler:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    total_count = len(sampler)
    if total_count < min_items:
        result["meta"] = {"reason": f"fewer than {min_items} occurrences of necessary fields"}
        return result

    statuses = {}
    passed_count = 0
    passed_examples = []
    failed_examples = []
    for sample in sampler:
        url = sample["value"]
        if url not in statuses:
            try:
                # Security: Potential SSRF via user-provided URL (within OCDS publication).
                with requests.get(
                    url,
                    timeout=settings.REQUESTS_TIMEOUT,
                    headers={"User-Agent": settings.USER_AGENT},
                    stream=True,
                ) as response:
                    if requests.codes.ok <= response.status_code < requests.codes.bad_request:
                        statuses[url] = "OK"
                    else:
                        statuses[url] = response.status_code
            except requests.RequestException:
                statuses[url] = "ERROR"

        sample["status"] = statuses[url]
        if sample["status"] == "OK":
            passed_examples.append(sample)
            passed_count += 1
        else:
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
