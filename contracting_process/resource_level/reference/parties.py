"""
Each referencing ``id`` is present and matches the ``id`` of exactly one party.
"""

from collections import Counter

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values


def calculate_path(item, path):
    result = get_empty_result_resource()

    test_values = get_values(item, path)
    if not test_values:
        result["meta"] = {"reason": "no reference is set"}
        return result

    values = get_values(item, "parties.id", value_only=True)
    party_id_counts_orig = Counter(values)
    party_id_counts_cast = Counter(map(str, values))

    application_count = 0
    pass_count = 0
    failed_paths = []
    for value in test_values:
        application_count += 1

        if "id" not in value["value"]:
            failed_paths.append({"path": value["path"], "reason": "reference has no id"})
        elif value["value"]["id"] not in party_id_counts_orig:
            if str(value["value"]["id"]) in party_id_counts_cast:
                failed_paths.append({"path": value["path"], "reason": "id values are not the same type"})
            else:
                failed_paths.append({"path": value["path"], "reason": "no party matches the referencing id"})
        elif party_id_counts_orig[value["value"]["id"]] > 1:
            failed_paths.append({"path": value["path"], "reason": "multiple parties match the referencing id"})
        else:
            pass_count += 1

    return complete_result_resource(result, application_count, pass_count, meta={"failed_paths": failed_paths})
