from tools.checks import get_empty_result_field

name = "number_checks"


def calculate(data, key):
    result = get_empty_result_field(name)

    if key not in data:
        result["result"] = False
        result["value"] = None
        result["reason"] = "missing key"
        return result

    value = data[key]
    if not is_number(value):
        result["result"] = False
        result["value"] = value
        result["reason"] = "not a number"
        return result

    if float(value) < 0:
        result["result"] = False
        result["value"] = value
        result["reason"] = "number is not positive"
        return result

    result["result"] = True
    return result


def is_number(value):
    if type(value) == complex:
        return False
    try:
        float(value)
    except ValueError:
        return False

    return True
