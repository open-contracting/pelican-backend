from tools.checks import field_level_check
from tools.codelists import get_identifier_scheme_codelist

name = "identifier_scheme"


def test(value):
    return value in get_identifier_scheme_codelist(), "not in codelist"


calculate = field_level_check(name, test)
