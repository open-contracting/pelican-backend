"""
The ``identifier`` of a related process whose ``scheme`` is 'ocid' matches the ``ocid`` of a compiled release.

The related process fields are:

-  ``contracts.relatedProcesses``
-  ``relatedProcesses``
"""

import itertools

from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import deep_get, get_values

version = 2.0
sample_size = 100


def add_item(scope, item, item_id):
    if not scope:
        scope = {
            "ocids": {},
            "related_processes": {},
            "meta": {
                "total_processed": 0,
                "total_passed": 0,
                "total_failed": 0,
                "passed_examples": ReservoirSampler(sample_size),
                "failed_examples": ReservoirSampler(sample_size),
            },
        }

    ocid = item["ocid"]

    if ocid:
        if ocid in scope["ocids"]:
            scope["ocids"][ocid]["found"] = True  # run before _add_example()
            for ref in scope["ocids"][ocid]["pending"]:
                scope = _add_example(scope, scope["related_processes"][ref])
                # Delete resolved references.
                del scope["related_processes"][ref]
            scope["ocids"][ocid]["pending"].clear()
        else:
            scope["ocids"][ocid] = {"pending": [], "found": True}

    for related_process in itertools.chain(
        get_values(item, "relatedProcesses"), get_values(item, "contracts.relatedProcesses")
    ):
        scheme = deep_get(related_process["value"], "scheme")
        if scheme != "ocid":
            continue

        ocid_reference = deep_get(related_process["value"], "identifier")
        if ocid_reference is None:
            continue

        example = {
            "item_id": item_id,
            "ocid": ocid,
            "related_path": related_process["path"],
            "related_ocid": ocid_reference,
        }

        seen = ocid_reference in scope["ocids"]
        if seen and scope["ocids"][ocid_reference]["found"]:
            scope = _add_example(scope, example)
        else:
            ref = (ocid, ocid_reference)
            if seen:
                scope["ocids"][ocid_reference]["pending"].append(ref)
            else:
                scope["ocids"][ocid_reference] = {"pending": [ref], "found": False}
            scope["related_processes"][ref] = example

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    for example in scope["related_processes"].values():
        scope = _add_example(scope, example)

    if not scope["meta"]["total_processed"]:
        result["meta"] = {"reason": "no pair of related processes sets necessary fields"}
        return result

    scope["meta"]["passed_examples"] = scope["meta"]["passed_examples"].sample
    scope["meta"]["failed_examples"] = scope["meta"]["failed_examples"].sample

    result["result"] = scope["meta"]["total_passed"] == scope["meta"]["total_processed"]
    result["value"] = 100 * scope["meta"]["total_passed"] / scope["meta"]["total_processed"]
    result["meta"] = scope["meta"]

    return result


def _add_example(scope, example):
    passed = scope["ocids"][example["related_ocid"]]["found"]

    if passed:
        scope["meta"]["total_passed"] += 1
        scope["meta"]["passed_examples"].process(example)
    else:
        scope["meta"]["total_failed"] += 1
        scope["meta"]["failed_examples"].process(example)
    scope["meta"]["total_processed"] += 1

    return scope
