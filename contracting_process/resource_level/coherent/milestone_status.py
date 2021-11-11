"""
If a milestone's status is unmet ('scheduled' or 'notMet'), then its dateMet is blank.
"""

from tools.checks import get_empty_result_resource
from tools.getter import deep_get, get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    milestones = []
    for path in ("planning", "tender", "contracts", "contracts.implementation"):
        milestones.extend(
            [
                v
                for v in get_values(item, f"{path}.milestones")
                if deep_get(v["value"], "status") in ("scheduled", "notMet")
            ]
        )

    if not milestones:
        result["meta"] = {"reason": "no milestone is unmet"}
        return result

    application_count = 0
    pass_count = 0
    result["meta"] = {"references": []}
    for milestone in milestones:
        passed = not deep_get(milestone["value"], "dateMet")

        result["meta"]["references"].append(
            {"result": passed, "status": milestone["value"]["status"], "path": milestone["path"]}
        )

        application_count += 1
        if passed:
            pass_count += 1

    result["result"] = application_count == pass_count
    result["application_count"] = application_count
    result["pass_count"] = pass_count

    return result
