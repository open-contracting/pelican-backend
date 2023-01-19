import phonenumbers

from pelican.util.checks import field_quality_check

name = "telephone"


def test(value):
    try:
        number = phonenumbers.parse(value, None)
        return phonenumbers.is_possible_number(number), "incorrect format"
    except phonenumbers.NumberParseException as e:
        return False, f"incorrect format: {e}"


# phonenumbers.parse() errors on non-str input.
calculate = field_quality_check(name, test, require_type=str)
