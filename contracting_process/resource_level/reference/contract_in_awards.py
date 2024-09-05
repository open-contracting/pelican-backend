"""
Each contract's ``awardID`` is present and matches the ``id`` of exactly one award.
"""

from collections import Counter

from pelican.util.checks import complete_result_resource, get_empty_result_resource
from pelican.util.getter import deep_has, get_values

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

        path = value["path"]
        if not deep_has(value["value"], "awardID"):
            failed_paths.append({"path": path, "awardID": None, "reason": "contract has no awardID"})
        else:
            award_id = value["value"]["awardID"]
            if award_id not in id_counts:
                if not ids:
                    failed_paths.append({"path": path, "awardID": award_id, "reason": "no award has an id"})
                elif str(award_id) in id_counts_str:
                    failed_paths.append(
                        {"path": path, "awardID": award_id, "reason": "id is not the same type as awardID"}
                    )
                else:
                    failed_paths.append({"path": path, "awardID": award_id, "reason": "no award matches the awardID"})
            elif id_counts[award_id] > 1:
                failed_paths.append(
                    {"path": path, "awardID": award_id, "reason": "multiple awards match the awardID"}  # (same type)
                )
            # Multiple matches across different types are currently designed to pass. (This assumes users do not coerce
            # IDs to strings.) If we change this to a failure, uncomment the following lines.
            #
            # > elif id_counts_str[str(award_id)] > 1:
            # >     failed_paths.append(
            # >       {"path": path, "awardID": award_id, "reason": "multiple awards match the awardID (types differ)"}
            # >     )
            else:
                pass_count += 1

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
