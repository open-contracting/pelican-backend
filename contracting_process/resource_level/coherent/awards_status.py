"""
If an award's status is inactive ('pending', 'cancelled', 'unsuccessful'), then no contract's awardID matches the
award's id.
"""

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_get, deep_has, get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    awards = [
        v
        for v in get_values(item, "awards")
        if deep_has(v["value"], "id") and deep_get(v["value"], "status") in ("pending", "cancelled", "unsuccessful")
    ]

    if not awards:
        result["meta"] = {"reason": "no award with an id is inactive"}
        return result

    contracts_award_ids = get_values(item, "contracts.awardID", value_only=True)

    application_count = 0
    pass_count = 0
    result["meta"] = {"processed_awards": []}
    for award in awards:
        # Note: Don't cast IDs to string for comparison. Users should be able to match IDs without doing so.
        passed = award["value"]["id"] not in contracts_award_ids

        result["meta"]["processed_awards"].append(
            {"path": award["path"], "id": award["value"]["id"], "result": passed}
        )

        application_count += 1
        if passed:
            pass_count += 1

    return complete_result_resource(result, application_count, pass_count)
