from tools.checks import field_quality_check
from tools.codelists import get_media_type_codelist

name = "document_format_codelist"


def test(value):
    return value in get_media_type_codelist(), "not in codelist"


calculate = field_quality_check(name, test)
