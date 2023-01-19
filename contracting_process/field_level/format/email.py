from validate_email import validate_email

from pelican.util.checks import field_quality_check

name = "email"


def test(value):
    return validate_email(value), "incorrect format"


# validate_email() errors on non-str input.
calculate = field_quality_check(name, test, require_type=str)
