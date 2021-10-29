from tools.checks import get_empty_result_field
from tools.codelists import get_ocid_prefix_codelist

name = "ocid_prefix_check"


def calculate(data, key):
    result = get_empty_result_field(name)

    if key not in data:
        result["result"] = False
        result["value"] = None
        result["reason"] = "missing key"
        return result

    ocid = data[key]
    if type(ocid) != str or not ocid:
        result["result"] = False
        result["value"] = ocid
        result["reason"] = "wrong ocid"
        return result

    codes = get_ocid_prefix_codelist()
    if ocid.startswith(codes):
        result["result"] = True
        return result

    result["result"] = False
    result["value"] = ocid
    result["reason"] = "wrong ocid"
    return result
