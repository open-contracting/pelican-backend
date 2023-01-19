"""
If the ``tender.procurementMethod`` is 'direct', then the ``tender.numberOfTenderers`` is at most 1.
"""

from tools.checks import complete_result_resource_pass_fail, get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    procurement_method_values = get_values(item, "tender.procurementMethod", value_only=True)
    number_of_tenderers_values = get_values(item, "tender.numberOfTenderers", value_only=True)

    if not procurement_method_values or not number_of_tenderers_values:
        result["meta"] = {"reason": "procurementMethod or numberOfTenderers is not set"}
        return result

    procurement_method = procurement_method_values[0]
    number_of_tenderers = number_of_tenderers_values[0]

    if procurement_method != "direct":
        result["meta"] = {"reason": "procurementMethod is not direct"}
        return result

    return complete_result_resource_pass_fail(
        result, number_of_tenderers == 0 or number_of_tenderers == 1, {"numberOfTenderers": number_of_tenderers}
    )
