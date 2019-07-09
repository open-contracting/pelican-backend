def exists(data, key):
    if key in data:
        return {"result": True}

    return {
        "result": False,
        "value": None,
        "reason": "missing key"
    }


def non_empty(data, key):
    if key not in data:
        return {
            "result": False,
            "value": None,
            "reason": "missing key"
        }

    if type(data) is dict and type(data[key]) is dict and not data[key]:
        return {
            "result": False,
            "value": data[key],
            "reason": "empty dictionary"
        }

    if type(data) is dict and type(data[key]) is list and not data[key]:
        return {
            "result": False,
            "value": data[key],
            "reason": "empty list"
        }

    if data[key]:
        return {"result": True}

    return {
        "result": False,
        "value": data[key],
        "reason": "empty"
    }
