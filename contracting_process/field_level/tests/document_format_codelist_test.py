
from contracting_process.field_level.document_format_codelist import calculate
from tools.helpers import is_subset_dict

"""
author: Iaroslav Kolodka

The file contains tests for contracting_process.field_level.document_format_codelist.document_format_codelist .

'test_ocid_prefix_ok' tests valid formas and exception (offline/print)
'test_ocid_prefix_failed' function checks cases with empty value and cases with incorrect format

"""


def test_ocid_prefix_ok():
    item1 = {
        "documents": [
            {
                "format": "application/AML"
            }
        ]
    }
    item2 = {
        "documents": [
            {
                "format": "offline/print"
            }
        ]
    }

    assert is_subset_dict(
        {"result": True},
        calculate(item1, "documents")
    )
    assert is_subset_dict(
        {"result": True},
        calculate(item2, "documents")
    )


def test_ocid_prefix_failed():
    not_found_result = {
        "result": None,
        "value": None,
        "reason": "Document has no format",
    }
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
        not_found_result,
        calculate({"documents": [{}]}, "documents")
    )
    assert is_subset_dict(
        fail_result1,
        calculate({"documents": [{"format": None}]}, "documents")
    )
    assert is_subset_dict(
        fail_result2,
        calculate({"documents": [{"format": "lalala"}]}, "documents")
    )
