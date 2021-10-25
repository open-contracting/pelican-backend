from tools.checks import get_empty_result_resource

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    # completely missing tender value
    if "tender" not in item:
        result["result"] = None
        result["meta"] = {"reason": "missing tender key"}
        return result

    tender = item["tender"]

    if "tenderers" in tender and "numberOfTenderers" in tender and type(tender["tenderers"]) == list:
        passed = tender["numberOfTenderers"] == len(tender["tenderers"])

        result["result"] = passed
        result["application_count"] = 1
        result["pass_count"] = int(passed)

        if not passed:
            result["meta"] = {"numberOfTenderers": tender["numberOfTenderers"], "tenderers": tender["tenderers"]}

        return result

    # unable to compare, undefined
    result["result"] = None
    result["meta"] = {"reason": "incomplete data for comparsion"}
    return result
