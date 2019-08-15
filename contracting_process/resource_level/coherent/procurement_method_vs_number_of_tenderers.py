from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    procurement_method = get_values(item, "tender.procurementMethod", value_only=True)
    number_of_tenderers = get_values(item, "tender.numberOfTenderers", value_only=True)

    if not procurement_method or not number_of_tenderers:
        # completely missing tender value
        result["result"] = None
        result["meta"] = {"reason": "incomplete data for check"}
        return result

    procurement_method = procurement_method[0]
    number_of_tenderers = number_of_tenderers[0]

    if procurement_method == "direct":
        if number_of_tenderers == 0 or number_of_tenderers == 1:
            result["result"] = True
            result["application_count"] = 1
            result["pass_count"] = 1
            result["meta"] = None
        else:
            result["result"] = False
            result["application_count"] = 1
            result["pass_count"] = 0
            result["meta"] = {"numberOfTenderers": number_of_tenderers}

        return result

    # unable to compare, undefined
    result["result"] = None
    result["meta"] = {"reason": "non-direct procurement method"}
    return result
