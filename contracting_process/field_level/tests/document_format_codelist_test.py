from contracting_process.field_level.document_format_codelist import document_format_codelist

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
    assert document_format_codelist(item1, "documents") == {"result": True}
    assert document_format_codelist(item2, "documents") == {"result": True}


def test_ocid_prefix_failed():
    fail_result = {
        "result": False,
        "value": None,
        "reason": "wrong file format"
    }
    not_found_result = {
        "result": None,
        "value": None,
        "reason": "Document has no format",
    }
    assert document_format_codelist({"documents": [{}]}, "documents") == not_found_result
    assert document_format_codelist({"documents": [{"format": None}]}, "documents") == fail_result
    fail_result["value"] = "lalala"
    assert document_format_codelist({"documents": [{"format": "lalala"}]}, "documents") == fail_result
