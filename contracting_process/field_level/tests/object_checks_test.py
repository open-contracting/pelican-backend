from contracting_process.field_level.object_checks import exists, non_empty


def test_exists():
    assert exists({"lang": "en"}, "lang") == {"result": True}
    assert exists({""}, "") == {"result": True}
    assert exists({"lang": "en"}, "lang2") == {"result": False, "value": None, "reason": "missing key"}
    assert exists({}, "lang2") == {"result": False, "value": None, "reason": "missing key"}
    assert exists({}, "") == {"result": False, "value": None, "reason": "missing key"}


def test_non_empty():
    assert non_empty({"lang": "en"}, "lang") == {"result": True}
    assert non_empty({"lang": ""}, "lang") == {"result": False, "value": "", "reason": "empty"}
    assert non_empty({"lang": []}, "lang") == {"result": False, "value": [], "reason": "empty list"}
    assert non_empty({"lang": {}}, "lang") == {"result": False, "value": {}, "reason": "empty dictionary"}
    assert non_empty({"lang": {}}, "lang2") == {"result": False, "value": None, "reason": "missing key"}
