from contracting_process.field_level.language import right_code


def test_lang_code_ok():
    assert right_code({"lang": "en"}, "lang") == {"result": True}


def test_lang_code_failed():
    assert right_code({"lang": "EN"}, "lang") == {"result": False, "value": "EN", "reason": "incorrect formatting"}
    assert right_code({"lang": "eN"}, "lang") == {"result": False, "value": "eN", "reason": "incorrect formatting"}
    assert right_code({"lang": "xx"}, "lang") == {"result": False, "value": "xx", "reason": "country doesn`t exist"}
