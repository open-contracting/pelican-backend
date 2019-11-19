from contracting_process.field_level.checks.document_format_codelist import calculate
from tools.helpers import is_subset_dict


def test_format_ok():
    item1 = {
        "format": "application/AML"

    }
    item2 = {
        "format": "offline/print"

    }

    assert is_subset_dict(
        {"result": True},
        calculate(item1, "format")
    )
    assert is_subset_dict(
        {"result": True},
        calculate(item2, "format")
    )


def test_format_failed():
    fail_result = {
        "result": False,
        "value": "lalala",
        "reason": "wrong file format"
    }

    assert is_subset_dict(
        fail_result,
        calculate({"format": "lalala"}, "format")
    )
