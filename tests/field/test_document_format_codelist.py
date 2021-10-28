import contracting_process.field_level.checks.document_format_codelist as document_format_codelist
from tools.helpers import is_subset_dict


def test_passed():
    document_format_codelist.format_codelist = ["application/AML"]

    assert is_subset_dict(
        {"result": True},
        document_format_codelist.calculate({"format": "application/AML"}, "format"),
    )
    assert is_subset_dict(
        {"result": False},
        document_format_codelist.calculate({"format": "offline/print"}, "format"),
    )


def test_failed():
    document_format_codelist.format_codelist = []

    assert is_subset_dict(
        {"result": False, "value": "unknown", "reason": "wrong document format"},
        document_format_codelist.calculate({"format": "unknown"}, "format"),
    )
