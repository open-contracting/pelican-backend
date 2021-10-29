from tools.checks import field_level_check
from tools.codelists import get_language_codelist

name = "language"


def test(value):
    return value in get_language_codelist(), "not in codelist"


calculate = field_level_check(name, test)
