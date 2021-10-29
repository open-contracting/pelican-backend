from contracting_process.field_level.codelist.identifier_scheme import calculate
from tests import is_subset_dict


def test_passed():
    assert is_subset_dict({"result": True}, calculate({"scheme": "XI-LEI"}, "scheme"))


def test_failed():
    assert is_subset_dict(
        {"result": False, "value": "b", "reason": "not in codelist"},
        calculate({"scheme": "b"}, "scheme"),
    )
    assert is_subset_dict(
        {"result": False, "value": None, "reason": "not in codelist"},
        calculate({"scheme": None}, "scheme"),
    )
