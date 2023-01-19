"""
Each reference has the same value for its ``name`` field as the party it references.

The test is skipped if every referencing ``id`` is missing or if none matches the ``id`` of exactly one party.

.. admonition:: Methodology notes

   -  A missing ``name`` is not an inconsistent value.
   -  ``id`` values are cast as ``str`` for matching.

.. seealso::

   :mod:`contracting_process.resource_level.reference.parties`, which fails in the skipped cases.
"""

from collections import Counter

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_has, get_values


def calculate(item, path):
    result = get_empty_result_resource()

    party_values = [
        v for v in get_values(item, "parties") if deep_has(v["value"], "id") and deep_has(v["value"], "name")
    ]

    # Guard against failure when accessing "id".
    if not party_values:
        result["meta"] = {"reason": "no party has an id and a name"}
        return result

    party_id_counts = Counter(str(v["value"]["id"]) for v in party_values)

    test_values = [
        v
        for v in get_values(item, path)
        if deep_has(v["value"], "id") and deep_has(v["value"], "name") and party_id_counts[str(v["value"]["id"])] == 1
    ]

    if not test_values:
        result["meta"] = {"reason": "no reference has an id and a name and matches exactly one party"}
        return result

    party_value_lookup = {str(v["value"]["id"]): v for v in party_values}

    application_count = 0
    pass_count = 0
    failed_paths = []
    for value in test_values:
        party = party_value_lookup[str(value["value"]["id"])]
        passed = value["value"]["name"] == party["value"]["name"]

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append(
                {
                    "party": {"path": party["path"], "id": party["value"]["id"], "name": party["value"]["name"]},
                    "reference": {"path": value["path"], "id": value["value"]["id"], "name": value["value"]["name"]},
                }
            )

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
