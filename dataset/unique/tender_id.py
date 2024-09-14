"""
Each ``tender.id`` is unique across the collection.

The test is skipped if the field is never present.
"""

import random

from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import deep_get

version = 2.0
sample_size = 100


def add_item(scope, item, item_id):
    if tender_id := deep_get(item, "tender.id", str):
        scope.setdefault(tender_id, [])
        scope[tender_id].append({"item_id": item_id, "ocid": item["ocid"]})

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version=version)

    if not scope:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    total_count = 0
    passed_count = 0
    passed_examples_sampler = ReservoirSampler(sample_size)
    failed_examples_sampler = ReservoirSampler(sample_size)

    for tender_id, items in scope.items():
        # Pick the "main" item that others repeat, at random.
        item = random.choice(items)  # noqa: S311
        sample = {"tender_id": tender_id, "ocid": item["ocid"], "item_id": item["item_id"], "all_items": items}
        repetitions = len(items)
        if repetitions == 1:
            passed_examples_sampler.process(sample)
            passed_count += 1
        else:
            failed_examples_sampler.process(sample)
        total_count += repetitions

    result["result"] = passed_count == total_count
    result["value"] = 100 * passed_count / total_count
    result["meta"] = {
        "total_processed": total_count,
        "total_passed": passed_count,
        "total_failed": total_count - passed_count,
        "passed_examples": passed_examples_sampler.sample,
        "failed_examples": failed_examples_sampler.sample,
    }

    return result
