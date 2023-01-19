"""
Each referencing ``id`` is present and matches the ``id`` of exactly one party.
"""

from collections import Counter

from pelican.util.checks import complete_result_resource, get_empty_result_resource
from pelican.util.getter import deep_has, get_values


def calculate_path(item, path):
    result = get_empty_result_resource()

    test_values = get_values(item, path)
    if not test_values:
        result["meta"] = {"reason": "no reference is set"}
        return result

    ids = get_values(item, "parties.id", value_only=True)
    id_counts = Counter(ids)
    id_counts_str = Counter(map(str, ids))

    application_count = 0
    pass_count = 0
    failed_paths = []
    for value in test_values:
        application_count += 1

        if not deep_has(value["value"], "id"):
            failed_paths.append({"path": value["path"], "reason": "reference has no id"})
        elif value["value"]["id"] not in id_counts:
            if str(value["value"]["id"]) in id_counts_str:
                failed_paths.append({"path": value["path"], "reason": "id values are not the same type"})
            else:
                failed_paths.append({"path": value["path"], "reason": "no party matches the referencing id"})
        elif id_counts[value["value"]["id"]] > 1:
            # Note: Multiple matches across different types currently pass.
            failed_paths.append({"path": value["path"], "reason": "multiple parties match the referencing id"})
        else:
            pass_count += 1

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
