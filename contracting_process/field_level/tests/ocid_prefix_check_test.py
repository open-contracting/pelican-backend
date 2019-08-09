from contracting_process.field_level.ocid_prefix_check import right_format


def test_right_format_ok():
    assert right_format({"ocid": "ocds-a2ef3d"}, "ocid") == {"result": True}
    assert right_format({"ocid": "ocds-a2ef3d123123123"}, "ocid") == {"result": True}


def test_right_format_failed():
    assert right_format({"ocid": "a000-a00000"}, "ocid") == {"result": False,
                                                             "value": "a000-a00000", "reason": "wrong ocid"}
    assert right_format({"ocid": 123123}, "ocid") == {"result": False, "value": 123123, "reason": "wrong ocid"}
    assert right_format({}, "ocid") == {"result": False, "value": None, "reason": "missing key"}
    assert right_format({"ocid": ""}, "ocid") == {"result": False, "value": "", "reason": "wrong ocid"}
