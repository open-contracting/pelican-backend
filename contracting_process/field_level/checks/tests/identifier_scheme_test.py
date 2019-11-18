
from contracting_process.field_level.checks.identifier_scheme import calculate
from tools.helpers import is_subset_dict


def test_valid_value():
    item = {
        "scheme": "XI-PB"
    }
    assert is_subset_dict(
        {"result": True},
        calculate(item, "scheme")
    )


def test_invalid_values():
    item_with_invalid_scheme_value = {"scheme": "XI-PB-WWW"}

    assert is_subset_dict(
        {
            "result": False,
            "value": "XI-PB-WWW",
            "reason": "Value is not from org-id.guide"
        },
        calculate(item_with_invalid_scheme_value, "scheme")
    )
