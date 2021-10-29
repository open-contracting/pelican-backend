from tools.checks import get_empty_result_field
from tools.codelists import get_language_codelist

name = "language"


def calculate(item, key):
    result = get_empty_result_field(name)

    value = item[key]
    passed = value in get_language_codelist()

    result["result"] = passed
    if not passed:
        result["value"] = value
        result["reason"] = "not in codelist"

    return result
