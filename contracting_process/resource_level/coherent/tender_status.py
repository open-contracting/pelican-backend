"""
If tender.status is incomplete ('planning', 'planned', 'active', 'cancelled', 'unsuccessful' or 'withdrawn'), then
awards and contracts are blank.
"""

from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    tender_status = get_values(item, "tender.status", value_only=True)
    if not tender_status:
        result["meta"] = {"reason": "tender.status is not present"}
        return result

    tender_status = tender_status[0]
    if tender_status not in ("planning", "planned", "active", "cancelled", "unsuccessful", "withdrawn"):
        result["meta"] = {"reason": f"tender.status is {tender_status!r}"}
        return result

    contracts_count = len(get_values(item, "contracts", value_only=True))
    awards_count = len(get_values(item, "awards", value_only=True))

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
