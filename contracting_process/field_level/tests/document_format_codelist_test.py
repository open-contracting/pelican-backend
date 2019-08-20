from contracting_process.field_level.document_format_codelist import document_format_codelist

"""
author: Iaroslav Kolodka

The file contains tests for contracting_process.field_level.document_format_codelist.document_format_codelist .

'test_ocid_prefix_ok' tests valid formas and exception (offline/print)
'test_ocid_prefix_failed' function checks cases with empty value and cases with incorrect format

"""


def test_ocid_prefix_ok():
    item1 = {
        "document": {
            "format": "application/AML"
        }
    }
    item2 = {
        "document": {
            "format": "offline/print"
        }
    }
    assert document_format_codelist(item1, "document") == {"result": True}
    assert document_format_codelist(item2, "document") == {"result": True}


def test_ocid_prefix_failed():
    fail_result = {"result": False,
                   "value": None,
                   "reason": "wrong file format"}
    assert document_format_codelist({"document": {}}, "document") == fail_result
    assert document_format_codelist({"document": {"format": None}}, "document") == fail_result
    fail_result["value"] = "lalala"
    assert document_format_codelist({"document": {"format": "lalala"}}, "document") == fail_result
