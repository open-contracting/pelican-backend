import pycountry


def right_code(data, key):
    value = data[key]
    if type(value) != str or len(value) != 2:
        return {"result": False,
                "value": value,
                "reason": "incorrect formatting"}
    for char in value:
        if not char.islower():
            return {"result": False,
                    "value": value,
                    "reason": "incorrect formatting"}
    language = pycountry.languages.get(alpha_2=value)
    if language is None:
        return {"result": False,
                "value": value,
                "reason": "country doesn`t exist"}
    return {"result": True}
