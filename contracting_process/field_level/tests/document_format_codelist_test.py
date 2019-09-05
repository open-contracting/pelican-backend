from contracting_process.field_level.document_format_codelist import document_format_codelist

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
    assert document_format_codelist(item1, "format") == {"result": True}
    assert document_format_codelist(item2, "format") == {"result": True}


def test_ocid_prefix_failed():
    fail_result = {
        "result": False,
        "value": None,
        "reason": "wrong file format"
    }
    assert document_format_codelist({"format": None}, "format") == fail_result
    fail_result["value"] = "lalala"
    assert document_format_codelist({"format": "lalala"}, "format") == fail_result
