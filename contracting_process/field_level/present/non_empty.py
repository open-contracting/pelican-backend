from tools.checks import get_empty_result_field

name = "non_empty"


def calculate(data, key):
    result = get_empty_result_field(name)

    if key not in data:
        result["result"] = False
        result["value"] = None
        result["reason"] = "missing key"
        return result

    if type(data) is dict and type(data[key]) is dict and not data[key]:
        result["result"] = False
        result["value"] = data[key]
        result["reason"] = "empty dictionary"
        return result

    if type(data) is dict and type(data[key]) is list and not data[key]:
        result["result"] = False
        result["value"] = data[key]
        result["reason"] = "empty list"
        return result

    if type(data) is dict and type(data[key]) is str and not data[key]:
        result["result"] = False
        result["value"] = data[key]
        result["reason"] = "empty string"
        return result

    if data[key] is None:
        result["result"] = False
        result["value"] = data[key]
        result["reason"] = "null value"
        return result

    result["result"] = True
    return result
