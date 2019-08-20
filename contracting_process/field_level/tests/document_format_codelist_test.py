from contracting_process.field_level.document_format_codelist import document_format_codelist

"""
author: Iaroslav Kolodka

"""
item = {}


def test():
    assert document_format_codelist(item, "key") == {"result": True}
