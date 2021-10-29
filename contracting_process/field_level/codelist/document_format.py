from tools.checks import get_empty_result_field
from tools.codelists import get_media_type_codelist

name = "document_format_codelist"


def calculate(item, key):
    result = get_empty_result_field(name)

    value = item[key]
    passed = value in get_media_type_codelist()

    result["result"] = passed
    if not passed:
        result["value"] = value
        result["reason"] = "not in codelist"

    return result
