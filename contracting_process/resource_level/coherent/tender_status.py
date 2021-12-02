"""
If tender.status is incomplete ('planning', 'planned', 'active', 'cancelled', 'unsuccessful' or 'withdrawn'), then
awards and contracts are blank.
"""

from tools.checks import get_empty_result_resource
from tools.getter import deep_get

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    status = deep_get(item, "tender.status")
    if not status:
        result["meta"] = {"reason": "tender.status is blank"}
        return result
    if status not in ("planning", "planned", "active", "cancelled", "unsuccessful", "withdrawn"):
        result["meta"] = {"reason": f"tender.status is {status!r}"}
        return result

    contracts_count = len(deep_get(item, "contracts", list))
    awards_count = len(deep_get(item, "awards", list))

    if contracts_count or awards_count:
        result["result"] = False
        result["application_count"] = 1
        result["pass_count"] = 0
        result["meta"] = {"contracts_count": contracts_count, "awards_count": awards_count}
        return result

    result["result"] = True
    result["application_count"] = 1
    result["pass_count"] = 1
    result["meta"] = None
    return result
