import random
from collections import defaultdict

from tools.checks import get_empty_result_dataset
from tools.getter import get_values
from tools.helpers import ReservoirSampler

version = 2.0


def add_item(scope, item, item_id):
    if not scope:
        scope = {"tender_id_mapping": defaultdict(list)}

    ocid = item["ocid"]
    values = get_values(item, "tender.id", value_only=True)
    if not values:
        return scope

    tender_id = str(values[0])
    scope["tender_id_mapping"][tender_id].append(
        {
            "ocid": item["ocid"],
            "item_id": item_id,
        }
    )

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version=version)

    if not scope or not scope["tender_id_mapping"]:
        result["meta"] = {"reason": "there are no tenders with check-specific properties"}
        return result

    result["meta"] = {
        "passed_examples": [],
        "failed_examples": [],
        "total_processed": None,
        "total_passed": None,
        "total_failed": None,
    }

    relevant_releases_count = sum(len(v) for v in scope["tender_id_mapping"].values())
    passed_releases_count = sum(len(v) for v in scope["tender_id_mapping"].values() if len(v) == 1)
    if relevant_releases_count == passed_releases_count:
        result["result"] = True
    else:
        result["result"] = False

    passed_examples_sampler = ReservoirSampler(100)
    failed_examples_sampler = ReservoirSampler(100)
    for tender_id, items in scope["tender_id_mapping"].items():
        main_item = random.choice(items)
        sample = {
            "tender_id": tender_id,
            "ocid": main_item["ocid"],
            "item_id": main_item["item_id"],
            "all_items": items,
        }
        if len(items) == 1:
            passed_examples_sampler.process(sample)
        else:
            failed_examples_sampler.process(sample)

    result["meta"]["passed_examples"] = passed_examples_sampler.retrieve_samples()
    result["meta"]["failed_examples"] = failed_examples_sampler.retrieve_samples()

    result["value"] = 100 * passed_releases_count / relevant_releases_count
    result["meta"]["total_processed"] = relevant_releases_count
    result["meta"]["total_passed"] = passed_releases_count
    result["meta"]["total_failed"] = relevant_releases_count - passed_releases_count

    return result
