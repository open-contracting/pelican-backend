from contracting_process.field_level.ocid_prefix_check import ocid_prefix


def test_ocid_prefix_ok():
    assert ocid_prefix({"ocid": "ocds-a2ef3d"}, "ocid") == {"result": True}
    assert ocid_prefix({"ocid": "ocds-a2ef3d123123123"}, "ocid") == {"result": True}


def test_ocid_prefix_failed():
    assert ocid_prefix({"ocid": "a000-a00000"}, "ocid") == {"result": False,
                                                            "value": "a000-a00000", "reason": "wrong ocid"}
    assert ocid_prefix({"ocid": 123123}, "ocid") == {"result": False, "value": 123123, "reason": "wrong ocid"}
    assert ocid_prefix({}, "ocid") == {"result": False, "value": None, "reason": "missing key"}
    assert ocid_prefix({"ocid": ""}, "ocid") == {"result": False, "value": "", "reason": "wrong ocid"}
