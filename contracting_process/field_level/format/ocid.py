from tools.checks import field_level_check
from tools.codelists import get_ocid_prefix_codelist

name = "ocid_prefix_check"


def test(value):
    return value.startswith(get_ocid_prefix_codelist()), "ocid prefix not in codelist"


# startswith is a str method.
calculate = field_level_check(name, test, require_type=str)
