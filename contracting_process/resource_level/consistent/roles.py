"""
Each referenced party has a corresponding role in its ``roles`` array.

The test is skipped if every referencing ``id`` is missing or if none matches the ``id`` of exactly one party.

.. admonition:: Methodology notes

   -  ``id`` values are cast as ``str`` for matching.

.. seealso::

   :mod:`contracting_process.resource_level.reference.parties`, which fails in the skipped cases.
"""

from collections import Counter

from pelican.util.checks import complete_result_resource, get_empty_result_resource
from pelican.util.getter import deep_get, deep_has, get_values

version = 1.0


def calculate_path_role(item, path, role):
    result = get_empty_result_resource(version)

    party_values = [v for v in get_values(item, "parties") if deep_has(v["value"], "id")]

    # Guard against failure when accessing "id".
    if not party_values:
        result["meta"] = {"reason": "no party has an id"}
        return result

    party_id_counts = Counter(str(v["value"]["id"]) for v in party_values)

    test_values = [
        v for v in get_values(item, path) if deep_has(v["value"], "id") and party_id_counts[str(v["value"]["id"])] == 1
    ]

    if not test_values:
        result["meta"] = {"reason": "no reference has an id and matches exactly one party"}
        return result

    party_value_lookup = {str(v["value"]["id"]): v for v in party_values}

    application_count = 0
    pass_count = 0
    failed_paths = []
    for value in test_values:
        party = party_value_lookup[str(value["value"]["id"])]
        roles = deep_get(party["value"], "roles", list)
        passed = role in roles

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append(
                {
                    "party": {"path": party["path"], "id": party["value"]["id"], "roles": roles},
                    "reference": {"path": value["path"], "id": value["value"]["id"], "role": role},
                }
            )

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
