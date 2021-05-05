from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0

"""
author: Iaroslav Kolodka

This check is calculated by application of
"milestone.status.coherent"(https://gitlab.com/datlab/ocp/dqt/wikis/Data-quality-checks/Resource-level-checks/milestone.status.coherent)
rule on all instances of $ref: "#/definitions/Milestone" from

- planning.milestones[]
- tender.milestones[]
- contracts[i].milestones[]
- contracts[i].implementation.milestones[]

parametr: testing JSON

"""


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
                statuses = get_values(milestone["value"], "properties.status", True)
                date_met = get_values(milestone["value"], "properties.dateMet", True)
                for status in statuses:  # because 'get_values' return array of values
                    if status in ("scheduled", "notMet"):
                        application_count += 1
                        if not date_met or not date_met[0]:
                            passed = True
                            pass_count += 1
                        else:
                            passed = False
                        result["meta"]["references"].append(
                            {"result": passed, "status": status, "path": milestone["path"]}
                        )
                    break  # there should be only one status
        if application_count > 0:  # else: None
            result["result"] = application_count == pass_count

    result["application_count"] = application_count
    result["pass_count"] = pass_count
    return result
