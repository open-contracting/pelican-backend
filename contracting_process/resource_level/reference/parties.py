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

        path = value["path"]
        if not deep_has(value["value"], "id"):
            failed_paths.append({"path": path, "id": None, "reason": "reference has no id"})
        else:
            ident = value["value"]["id"]
            if ident not in id_counts:
                if not ids:
                    failed_paths.append({"path": path, "id": ident, "reason": "no party has an id"})
                elif str(ident) in id_counts_str:
                    failed_paths.append({"path": path, "id": ident, "reason": "id values are not the same type"})
                else:
                    failed_paths.append({"path": path, "id": ident, "reason": "no party matches the referencing id"})
            elif id_counts[ident] > 1:
                failed_paths.append({"path": path, "id": ident, "reason": "multiple parties match the referencing id"})
            # Multiple matches across different types are currently designed to pass. (This assumes users do not coerce
            # IDs to strings.) If we change this to a failure, uncomment the following lines.
            #
            # > elif id_counts_str[str(ident)] > 1:
            # >     failed_paths.append(
            # >       {"path": path, "id": ident, "reason": "multiple parties match the referencing id (types differ)"}
            # >     )
            else:
                pass_count += 1

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
