

def positive_number(data, key):
    if key not in data:
        return {
            "result": False,
            "value": None,
            "reason": "missing key"
        }
    value = data[key]
    if not is_number(value):
        return {
            "result": False,
            "value": value,
            "reason": "not a number"
        }
    if float(value) < 0:
        return {
            "result": False,
            "value": value,
            "reason": "number is not positive"
        }
    return {"result": True}


def is_number(value):
    if type(value) == complex:
        return False
    try:
        float(value)
    except ValueError:
        return False
    return True
