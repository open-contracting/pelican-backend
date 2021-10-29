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
    meta = {}
    if milestones:
        meta = {"references": []}
        for milestone in milestones:
            passed = None
            status = None
            if "value" in milestone and milestone["value"]:
                statuses = get_values(milestone["value"], "status", True)
                date_met = get_values(milestone["value"], "dateMet", True)
                for status in statuses:  # because 'get_values' return array of values
                    if status in ("scheduled", "notMet"):
                        passed = not date_met or not date_met[0]

                        application_count += 1
                        if passed:
                            pass_count += 1

                        meta["references"].append({"result": passed, "status": status, "path": milestone["path"]})
                    break  # there should be only one status

    if application_count:
        result["result"] = application_count == pass_count
        result["application_count"] = application_count
        result["pass_count"] = pass_count
        result["meta"] = meta
    else:
        result["meta"] = {"reason": "criteria not met"}

    return result
