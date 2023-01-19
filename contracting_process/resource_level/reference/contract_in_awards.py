"""
Each contract's ``awardID`` is present and matches the ``id`` of exactly one award.
"""

from collections import Counter

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_has, get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    test_values = get_values(item, "contracts")
    if not test_values:
        result["meta"] = {"reason": "no contract is set"}
        return result

    ids = get_values(item, "awards.id", value_only=True)
    id_counts = Counter(ids)
    id_counts_str = Counter(map(str, ids))

    application_count = 0
    pass_count = 0
    failed_paths = []
    for value in test_values:
        application_count += 1

        if not deep_has(value["value"], "awardID"):
            failed_paths.append({"path": value["path"], "reason": "contract has no awardID"})
        elif value["value"]["awardID"] not in id_counts:
            if str(value["value"]["awardID"]) in id_counts_str:
                failed_paths.append({"path": value["path"], "reason": "id is not the same type as awardID"})
            else:
                failed_paths.append({"path": value["path"], "reason": "no award matches the awardID"})
        elif id_counts[value["value"]["awardID"]] > 1:
            # Note: Multiple matches across different types currently pass.
            failed_paths.append({"path": value["path"], "reason": "multiple awards match the awardID"})
        else:
            pass_count += 1

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
