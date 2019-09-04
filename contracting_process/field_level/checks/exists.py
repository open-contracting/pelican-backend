
from tools.checks import get_empty_result_field

name = "exists"


def calculate(data, key):
    result = get_empty_result_field(name)

    if key in data:
        result["result"] = True
        return result

    result["result"] = False
    result["value"] = None
    result["reason"] = "missing key"
    return result
