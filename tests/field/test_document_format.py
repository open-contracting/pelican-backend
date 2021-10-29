from contracting_process.field_level.codelist.document_format import calculate
from tests import is_subset_dict


def test_passed():
    assert is_subset_dict(
        {"result": True},
        calculate({"format": "application/AML"}, "format"),
    )
    assert is_subset_dict(
        {"result": True},
        calculate({"format": "offline/print"}, "format"),
    )


def test_failed():
    assert is_subset_dict(
        {"result": False, "value": "unknown", "reason": "wrong document format"},
        calculate({"format": "unknown"}, "format"),
    )
