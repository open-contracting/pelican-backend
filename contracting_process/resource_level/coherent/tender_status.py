"""
If ``tender.status`` is incomplete, then ``awards`` and ``contracts`` are blank.

Incomplete statuses are: 'planning', 'planned', 'active', 'cancelled', 'unsuccessful' are 'withdrawn'.
"""

from pelican.util.checks import complete_result_resource_pass_fail, get_empty_result_resource
from pelican.util.getter import deep_get

version = 1.0
applicable_statuses = {"planning", "planned", "active", "cancelled", "unsuccessful", "withdrawn"}


def calculate(item):
    result = get_empty_result_resource(version)

    status = deep_get(item, "tender.status")
    if not status:
        result["meta"] = {"reason": "tender.status is blank"}
        return result
    if status not in applicable_statuses:
        result["meta"] = {"reason": f"tender.status is {status!r}"}
        return result

    contracts_count = len(deep_get(item, "contracts", list))
    awards_count = len(deep_get(item, "awards", list))

    return complete_result_resource_pass_fail(
        result,
        not contracts_count and not awards_count,
        {"contracts_count": contracts_count, "awards_count": awards_count},
    )
