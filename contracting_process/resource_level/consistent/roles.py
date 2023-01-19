"""
Each referenced party has a corresponding role in its ``roles`` array.

The test is skipped if every referencing ``id`` is missing or if none matches the ``id`` of exactly one party.

.. admonition:: Methodology notes

   -  ``id`` values are cast as ``str`` for matching.

.. seealso::

   :mod:`contracting_process.resource_level.reference.parties`, which fails in the skipped cases.
"""

from collections import Counter

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_get, get_values

version = 1.0


def calculate_path_role(item, path, role):
    result = get_empty_result_resource(version)

    party_values = [v for v in get_values(item, "parties") if "id" in v["value"]]

    # Guard against failure when accessing "id".
    if not party_values:
        result["meta"] = {"reason": "no party has an id"}
        return result

    party_id_counts = Counter(str(v["value"]["id"]) for v in party_values)

    test_values = [
        v for v in get_values(item, path) if "id" in v["value"] and party_id_counts[str(v["value"]["id"])] == 1
    ]

    if not test_values:
        result["meta"] = {"reason": "no reference has an id and matches exactly one party"}
        return result

    party_value_lookup = {
        str(v["value"]["id"]): v for v in party_values if party_id_counts[str(v["value"]["id"])] == 1
    }

    application_count = 0
    pass_count = 0
    result["meta"] = {"references": []}
    for value in test_values:
        party = party_value_lookup[str(value["value"]["id"])]

        passed = role in deep_get(party["value"], "roles", list)
        application_count += 1
        if passed:
            pass_count += 1

        result["meta"]["references"].append(
            {
                "organization.id": str(value["value"]["id"]),
                "expected_role": role,
                "referenced_party_path": party["path"],
                "referenced_party": party["value"],
                "resource_path": value["path"],
                "resource": value["value"],
                "result": passed,
            }
        )

    return complete_result_resource(result, application_count, pass_count)
