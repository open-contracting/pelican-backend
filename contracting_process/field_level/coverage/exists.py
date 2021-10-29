from tools.checks import field_coverage_check

name = "exists"


def test(item, key):
    return key in item, "not set"


calculate = field_coverage_check(name, test)
