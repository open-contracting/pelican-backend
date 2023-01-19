from pelican.util.checks import field_quality_check

name = "document_description_length"
max_length = 250


def test(value):
    return len(value) <= max_length, f"length greater than {max_length}"


# len() errors on non-str input.
calculate = field_quality_check(name, test, require_type=str, return_value=len)
