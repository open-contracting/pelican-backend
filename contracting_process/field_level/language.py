import pycountry


def language_code(data, key):
    value = data[key]
    if type(value) != str or len(value) != 2:
        return {"result": False,
                "value": value,
                "reason": "incorrect formatting"}

    if not value.islower():
        return {"result": False,
                "value": value,
                "reason": "language code must be in lower case"}

    language = pycountry.languages.get(alpha_2=value)
    if language is None:
        return {"result": False,
                "value": value,
                "reason": "country doesn`t exist"}
    return {"result": True}
