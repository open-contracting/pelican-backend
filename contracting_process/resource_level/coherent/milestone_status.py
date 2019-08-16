from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)
    milestones = get_values(item, "planning.milestones")
    milestones.extend(get_values(item, "tender.milestones"))
    milestones.extend(get_values(item, "contracts.milestones"))
    milestones.extend(get_values(item, "contracts.implementation.milestones"))
    application_count = 0
    pass_count = 0
    result["meta"] = {}
    if milestones:
        result["meta"] = {"references": []}
        for milestone in milestones:
            passed = None
            status = None
            if "value" in milestone and milestone["value"]:
                statuses = get_values(milestone["value"], "properties.status")
                date_met = get_values(milestone["value"], "properties.dateMet")
                for status in statuses:
                    if "value" in status and status["value"] is "scheduled" or status["value"] is "notMet":
                        application_count += 1
                        status = status["value"]
                        if not date_met:
                            passed = True
                            pass_count += 1
                        else:
                            passed = False
                        result["meta"]["references"].append(
                            {
                                "result": passed,
                                "status": status,
                                "path": milestone["path"]
                            }
                        )
        if application_count > 0:
            result["result"] = application_count == pass_count

    result["application_count"] = application_count
    result["pass_count"] = pass_count
    return result
