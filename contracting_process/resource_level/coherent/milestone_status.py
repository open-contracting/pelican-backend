from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)
    milestones = get_values(item, "planning.milestones")
    milestones.extend(get_values(item, "tender.milestones"))
    milestones.extend(get_values(item, "contracts.milestones"))
    milestones.extend(get_values(item, "contracts.implementation.milestones"))
    is_passed = None
    application_count = 0
    pass_count = 0
    result["meta"] = {}
    if milestones:
        result["meta"] = {"references": []}
        for milestone in milestones:
            application_count += 1
            is_passed = False
            status = None
            if "value" in milestone and milestone["value"]:
                statuses = get_values(milestone["value"], "properties.status")
                for status in statuses:
                    if "value" in status:
                        if status["value"] is "scheduled" or status["value"] is "notMet":
                            is_passed = True
                            pass_count += 1
                            status = status["value"]
                            break
            result["meta"]["references"].append(
                {
                    "result": is_passed,
                    "status": status,
                    "path": milestone["path"]
                }
            )
        result["result"] = application_count == pass_count
    else:
        result["result"] = None

    result["application_count"] = application_count
    result["pass_count"] = pass_count
    return result
