from tools.checks import complete_result_resource_pass_fail, get_empty_result_resource

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    if "tender" not in item:
        result["meta"] = {"reason": "missing tender key"}
        return result

    tender = item["tender"]

    if "tenderers" not in tender or "numberOfTenderers" not in tender or type(tender["tenderers"]) != list:
        result["meta"] = {"reason": "incomplete data for comparison"}
        return result

    return complete_result_resource_pass_fail(
        result,
        tender["numberOfTenderers"] == len(tender["tenderers"]),
        {"numberOfTenderers": tender["numberOfTenderers"], "tenderers": tender["tenderers"]},
    )
