"""
If a contract's ``status`` is unsigned ('pending' or 'cancelled'), then its ``implementation.transactions`` is blank.
"""

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_get, get_values

version = 1.0
applicable_statuses = {"pending", "cancelled"}


def calculate(item):
    result = get_empty_result_resource(version)

    contracts = [v for v in get_values(item, "contracts") if deep_get(v["value"], "status") in applicable_statuses]

    if not contracts:
        result["meta"] = {"reason": "no contract is unsigned"}
        return result

    application_count = 0
    pass_count = 0
    failed_paths = []
    for contract in contracts:
        transactions_count = len(deep_get(contract["value"], "implementation.transactions", list))
        passed = transactions_count == 0

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append({"path": contract["path"], "transactions_count": transactions_count})

    return complete_result_resource(result, application_count, pass_count, meta={"failed_paths": failed_paths})
