from contracting_process.field_level.checks.language import calculate
from tools.helpers import is_subset_dict


def test_lang_code_ok():
    assert is_subset_dict(
        {"result": True},
        calculate({"lang": "en"}, "lang")
    )


def test_lang_code_failed():
    assert is_subset_dict(
        {"result": False, "value": "EN", "reason": "language code must be in lower case"},
        calculate({"lang": "EN"}, "lang")
    )
    assert is_subset_dict(
        {"result": False, "value": "eN", "reason": "language code must be in lower case"},
        calculate({"lang": "eN"}, "lang")
    )
    assert is_subset_dict(
        {"result": False, "value": "xx", "reason": "country doesn`t exist"},
        calculate({"lang": "xx"}, "lang")
    )
