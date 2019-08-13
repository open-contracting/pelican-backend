from contracting_process.field_level.date_time import date_realistic


def test_date_realistic_ok():
    assert date_realistic({"date": "1971-05-05"}, "date") == {"result": True}
    assert date_realistic({"date": "1970-01-01"}, "date") == {"result": True}
    assert date_realistic({"date": "2050-01-01"}, "date") == {"result": True}


def test_date_realistic_failed():
    assert date_realistic({"date": ""}, "date") == {"result": False, "value": "", "reason": "incorrect date format"}
    assert date_realistic({"date": "abcabc"}, "date") == {"result": False,
                                                          "value": "abcabc", "reason": "incorrect date format"}
    assert date_realistic({"date": 123123}, "date") == {"result": False,
                                                        "value": 123123, "reason": "incorrect date format"}
    assert date_realistic({"date": "1969-5-5"}, "date") == {"result": False,
                                                            "value": "1969-5-5", "reason": "date is out of range"}
    assert date_realistic({"date": "2051-1-1"}, "date") == {"result": False,
                                                            "value": "2051-1-1", "reason": "date is out of range"}
