
from contracting_process.field_level.checks.document_format_codelist import calculate
from tools.helpers import is_subset_dict

""" The file contains tests for contracting_process.field_level.document_format_codelist.document_format_codelist .

    author: Iaroslav Kolodka

    'test_ocid_prefix_ok' tests valid formas and exception (offline/print)
    'test_ocid_prefix_failed' function checks cases with empty value and cases with incorrect format

"""


def test_ocid_prefix_ok():
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


def test_ocid_prefix_failed():
    fail_result1 = {
        "result": False,
        "value": None,
        "reason": "wrong file format"
    }
    fail_result2 = {
        "result": False,
        "value": "lalala",
        "reason": "wrong file format"
    }

    assert is_subset_dict(
        fail_result1,
        calculate({"format": None}, "format")
    )
    assert is_subset_dict(
        fail_result2,
        calculate({"format": "lalala"}, "format")
    )
