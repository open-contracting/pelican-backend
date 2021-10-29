from tools.checks import field_coverage_check

name = "non_empty"


def test(item, key):
    if key not in item:
        return False, "not set"

    value = item[key]

    if value is None:
        return False, "null value"
    if type(value) is dict and not value:
        return False, "empty object"
    if type(value) is list and not value:
        return False, "empty array"
    if type(value) is str and not value:
        return False, "empty string"

    return True, None


calculate = field_coverage_check(name, test)
