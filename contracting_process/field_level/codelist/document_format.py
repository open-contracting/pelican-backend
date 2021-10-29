from tools.checks import get_empty_result_field
from tools.codelists import get_media_type_codelist

name = "document_format_codelist"


def calculate(item, key):
    result = get_empty_result_field(name)
    result["result"] = False

    document_format = item[key]

    passed = document_format in get_media_type_codelist()
    result["result"] = passed

    if not passed:
        result["value"] = document_format
        result["reason"] = "wrong document format"

    return result
