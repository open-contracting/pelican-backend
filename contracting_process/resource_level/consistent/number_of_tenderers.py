"""
The value of the ``numberOfTenderers`` field is equal to the number of entries in the ``tenderers`` array.

The test is skipped if the ``tenderers`` field is not an array.
"""

from pelican.util.checks import complete_result_resource_pass_fail, get_empty_result_resource
from pelican.util.getter import deep_get

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    number_of_tenderers = deep_get(item, "tender.numberOfTenderers", float)
    if number_of_tenderers is None:
        result["meta"] = {"reason": "numberOfTenderers is non-numeric"}
        return result

    tenderers = deep_get(item, "tender.tenderers")

    if type(tenderers) != list:
        result["meta"] = {"reason": "tenderers is not an array"}
        return result

    return complete_result_resource_pass_fail(
        result,
        number_of_tenderers == len(tenderers),
        {"numberOfTenderers": item["tender"]["numberOfTenderers"], "tenderers": item["tender"]["tenderers"]},
    )
