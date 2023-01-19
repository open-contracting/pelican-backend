"""
If an award's ``status`` is inactive ('pending', 'cancelled', 'unsuccessful'), then no contract's ``awardID`` matches
the award's ``id``.
"""

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_get, deep_has, get_values

version = 1.0
applicable_statuses = {"pending", "cancelled", "unsuccessful"}


def calculate(item):
    result = get_empty_result_resource(version)

    awards = [
        v
        for v in get_values(item, "awards")
        if deep_get(v["value"], "status") in applicable_statuses and deep_has(v["value"], "id")
    ]

    if not awards:
        result["meta"] = {"reason": "no award with an id is inactive"}
        return result

    contracts_award_ids = {str(v) for v in get_values(item, "contracts.awardID", value_only=True)}

    application_count = 0
    pass_count = 0
    failed_paths = []
    for award in awards:
        passed = str(award["value"]["id"]) not in contracts_award_ids

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append({"path": award["path"], "id": award["value"]["id"]})

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
