from tools.checks import get_empty_result_field
from tools.codelists import get_identifier_scheme_codelist

name = "identifier_scheme"


def calculate(item, key):
    result = get_empty_result_field(name)

    value = item[key]
    passed = value in get_identifier_scheme_codelist()

    result["result"] = passed
    if not passed:
        result["value"] = value
        result["reason"] = "not in codelist"

    return result
