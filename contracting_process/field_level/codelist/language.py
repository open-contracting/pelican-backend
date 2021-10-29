from tools.checks import get_empty_result_field
from tools.codelists import get_language_codelist

name = "language"


def calculate(data, key):
    result = get_empty_result_field(name)

    value = data[key]
    if type(value) != str or len(value) != 2:
        result["result"] = False
        result["value"] = value
        result["reason"] = "incorrect formatting"
        return result

    if not value.islower():
        result["result"] = False
        result["value"] = value
        result["reason"] = "language code must be in lower case"
        return result

    if value not in get_language_codelist():
        result["result"] = False
        result["value"] = value
        result["reason"] = "country doesn`t exist"
        return result

    result["result"] = True
    return result
