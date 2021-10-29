from validate_email import validate_email

from tools.checks import field_level_check

name = "email"


def test(value):
    return validate_email(value), "incorrect format"


# validate_email errors on non-str input.
calculate = field_level_check(name, test, require_type=str)
