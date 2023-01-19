from pelican.util.checks import field_quality_check
from pelican.util.codelists import get_language_codelist

name = "language"


def test(value):
    return value in get_language_codelist(), "not in codelist"


calculate = field_quality_check(name, test)
