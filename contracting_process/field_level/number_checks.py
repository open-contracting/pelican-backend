import logging


def positive_number(data, key):
    logging.debug("Checking on correct number in {}", key)
    if key not in data:
        return {
            "result": False,
            "value": None,
            "reason": "missing key"
        }
    value = data[key]
    data_type = type(value)
    if data_type != int and data_type != float:
        return {
            "result": False,
            "value": value,
            "reason": "not a number"
        }
    if float(value) <= 0:
        return {
            "result": False,
            "value": value,
            "reason": "number is not positive"
        }
    return {"result": True}
