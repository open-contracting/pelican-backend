from contracting_process.field_level.codelist.language import calculate
from tests import is_subset_dict


def test_lang_code_ok():
    assert is_subset_dict({"result": True}, calculate({"lang": "en"}, "lang"))


def test_lang_code_failed():
    assert is_subset_dict(
        {"result": False, "value": "EN", "reason": "not in codelist"},
        calculate({"lang": "EN"}, "lang"),
    )
    assert is_subset_dict(
        {"result": False, "value": "eN", "reason": "not in codelist"},
        calculate({"lang": "eN"}, "lang"),
    )
    assert is_subset_dict(
        {"result": False, "value": "xx", "reason": "not in codelist"}, calculate({"lang": "xx"}, "lang")
    )
