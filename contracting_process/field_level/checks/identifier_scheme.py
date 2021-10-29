from tools.checks import get_empty_result_field
from tools.codelists import get_identifier_scheme_codelist

name = "identifier_scheme"


def calculate(item, key):
    result = get_empty_result_field(name)

    scheme = item[key]

    passed = scheme in get_identifier_scheme_codelist()
    result["result"] = passed

    if not passed:
        result["value"] = scheme
        result["reason"] = "wrong identifier scheme"

    return result
