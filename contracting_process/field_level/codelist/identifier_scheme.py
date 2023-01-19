from pelican.util.checks import field_quality_check
from pelican.util.codelists import get_identifier_scheme_codelist

name = "identifier_scheme"


def test(value):
    return value in get_identifier_scheme_codelist(), "not in codelist"


calculate = field_quality_check(name, test)
