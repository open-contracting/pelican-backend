"""
If the ``tender.procurementMethod`` is 'direct', then the ``tender.numberOfTenderers`` is at most 1.
"""

from tools.checks import complete_result_resource_pass_fail, get_empty_result_resource
from tools.getter import deep_get

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    number_of_tenderers = deep_get(item, "tender.numberOfTenderers", float)

    if number_of_tenderers is None:
        result["meta"] = {"reason": "numberOfTenderers is non-numeric"}
        return result

    procurement_method = deep_get(item, "tender.procurementMethod")

    if procurement_method != "direct":
        result["meta"] = {"reason": "procurementMethod is not direct"}
        return result

    return complete_result_resource_pass_fail(
        result,
        number_of_tenderers == 0 or number_of_tenderers == 1,
        {"numberOfTenderers": item["tender"]["numberOfTenderers"]},
    )
