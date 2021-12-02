"""
If a contract's status is unsigned ('pending' or 'cancelled'), then its implementation.transactions is blank.
"""

from tools.checks import get_empty_result_resource
from tools.getter import deep_get, get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    contracts = [
        v for v in get_values(item, "contracts") if deep_get(v["value"], "status") in ("pending", "cancelled")
    ]

    if not contracts:
        result["meta"] = {"reason": "no contract is unsigned"}
        return result

    application_count = 0
    pass_count = 0
    result["meta"] = {"processed_contracts": []}
    for contract in contracts:
        transactions_count = len(deep_get(contract["value"], "implementation.transactions", list))
        passed = transactions_count == 0

        result["meta"]["processed_contracts"].append(
            {"path": contract["path"], "transactions_count": transactions_count, "result": passed}
        )

        application_count += 1
        if passed:
            pass_count += 1

    result["result"] = application_count == pass_count
    result["application_count"] = application_count
    result["pass_count"] = pass_count

    return result
