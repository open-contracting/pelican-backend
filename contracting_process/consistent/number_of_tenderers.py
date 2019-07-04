from tools.checks import get_empty_result

version = 1.0


def calculate(item):
    result = get_empty_result(version)

    # completely missing tender value
    if "tender" not in item:
        result["result"] = None
        result["meta"] = {"reason": "missing tender key"}
        return result

    tender = item["tender"]

    if "tenderers" in tender and "numberOfTenderers" in tender and type(tender["tenderers"]) == list:
        # everything is set, we can compare
        if tender["numberOfTenderers"] == len(tender["tenderers"]):
            result["result"] = True
            result["value"] = 100
        else:
            result["result"] = False
            result["value"] = 0
            result["meta"] = {
                "numberOfTenderers": tender["numberOfTenderers"],
                "tenderers": tender["tenderers"]
            }

        return result

    # unable to compare, undefined
    result["result"] = None
    result["value"] = None
    result["meta"] = {"reason": "incomplete data for comparsion"}
    return result
