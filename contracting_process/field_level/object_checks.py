def exists(data, key):
    if key in data:
        return {"result": True}

    return {
        "result": False,
        "value": None,
        "reason": "missing key"
    }


def non_empty(data, key):
    if data[key]:
        return {"result": True}

    return {
        "result": False,
        "value": data[key],
        "reason": "empty"
    }
