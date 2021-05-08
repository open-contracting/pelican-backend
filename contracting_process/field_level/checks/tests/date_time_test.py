from contracting_process.field_level.checks.date_time import calculate
from tools.helpers import is_subset_dict


def test_date_time_ok():
    assert is_subset_dict({"result": True}, calculate({"date": "1971-05-05"}, "date"))
    assert is_subset_dict({"result": True}, calculate({"date": "1970-01-01"}, "date"))
    assert is_subset_dict({"result": True}, calculate({"date": "2050-01-01"}, "date"))


def test_date_time_failed():
    assert is_subset_dict(
        {"result": False, "value": "", "reason": "incorrect date format"}, calculate({"date": ""}, "date")
    )
    assert is_subset_dict(
        {"result": False, "value": "abcabc", "reason": "incorrect date format"}, calculate({"date": "abcabc"}, "date")
    )
    assert is_subset_dict(
        {"result": False, "value": 123123, "reason": "incorrect date format"}, calculate({"date": 123123}, "date")
    )
    assert is_subset_dict(
        {"result": False, "value": "1969-5-5", "reason": "date is out of range"},
        calculate({"date": "1969-5-5"}, "date"),
    )
    assert is_subset_dict(
        {"result": False, "value": "2051-1-1", "reason": "date is out of range"},
        calculate({"date": "2051-1-1"}, "date"),
    )
