"""
The value of the ``numberOfTenderers`` field is equal to the number of entries in the ``tenderers`` array.

The test is skipped if the ``tenderers`` field is not an array.
"""

from tools.checks import complete_result_resource_pass_fail, get_empty_result_resource

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    if "tender" not in item:
        result["meta"] = {"reason": "tender is not set"}
        return result

    tender = item["tender"]

    if "tenderers" not in tender or "numberOfTenderers" not in tender or type(tender["tenderers"]) != list:
        result["meta"] = {"reason": "numberOfTenderers is not set or tenderers is not a list"}
        return result

    return complete_result_resource_pass_fail(
        result,
        tender["numberOfTenderers"] == len(tender["tenderers"]),
        {"numberOfTenderers": tender["numberOfTenderers"], "tenderers": tender["tenderers"]},
    )
