from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    procurement_method_values = get_values(item, "tender.procurementMethod", value_only=True)
    number_of_tenderers_values = get_values(item, "tender.numberOfTenderers", value_only=True)

    if not procurement_method_values or not number_of_tenderers_values:
        # completely missing tender value
        result["result"] = None
        result["meta"] = {"reason": "incomplete data for check"}
        return result

    procurement_method = procurement_method_values[0]
    number_of_tenderers = number_of_tenderers_values[0]

    if procurement_method == "direct":
        passed = number_of_tenderers == 0 or number_of_tenderers == 1

        result["result"] = passed
        result["application_count"] = 1
        result["pass_count"] = int(passed)

        if not passed:
            result["meta"] = {"numberOfTenderers": number_of_tenderers}

        return result

    # unable to compare, undefined
    result["result"] = None
    result["meta"] = {"reason": "non-direct procurement method"}
    return result
