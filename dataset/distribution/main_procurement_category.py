"""
No ``tender.mainProcurementCategory`` code occurs in more than 95% of cases.

The test is skipped if the field is never present. The codelist is closed.
"""

from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import deep_get

version = 1.0
sample_size = 100


def add_item(scope, item, item_id):
    if category := deep_get(item, "tender.mainProcurementCategory", str):
        scope.setdefault(category, ReservoirSampler(sample_size))
        scope[category].process({"item_id": item_id, "ocid": item["ocid"]})

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope:
        result["meta"] = {"reason": "no compiled releases set necessary fields"}
        return result

    total_count = sum(sampler.index for sampler in scope.values())
    sorted_scope = sorted(scope.items(), key=lambda item: item[1].index, reverse=True)
    passed = sorted_scope[0][1].index / total_count <= 0.95

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "shares": {
            category: {
                "share": sampler.index / total_count,
                "count": sampler.index,
                "examples": sampler.sample,
            }
            for category, sampler in sorted_scope
        }
    }

    return result
