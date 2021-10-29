from contracting_process.field_level.checks.number_checks import calculate
from tests import is_subset_dict


def test_ok():
    assert is_subset_dict({"result": True}, calculate({"number": 10}, "number"))
    assert is_subset_dict({"result": True}, calculate({"number": 10.0}, "number"))


def test_failed():
    assert is_subset_dict({"result": False, "value": None, "reason": "missing key"}, calculate({}, "number"))
    assert is_subset_dict(
        {"result": False, "value": None, "reason": "missing key"}, calculate({"name_of_value": 10}, "number")
    )
    assert is_subset_dict(
        {"result": False, "value": None, "reason": "missing key"}, calculate({"name_of_value": "value"}, "number")
    )
    assert is_subset_dict(
        {"result": False, "value": "value", "reason": "not a number"}, calculate({"number": "value"}, "number")
    )
    assert is_subset_dict(
        {"result": False, "value": 10j, "reason": "not a number"}, calculate({"number": 10j}, "number")
    )
    assert is_subset_dict({"result": True}, calculate({"number": 0}, "number"))
    assert is_subset_dict(
        {"result": False, "value": -1, "reason": "number is not positive"}, calculate({"number": -1}, "number")
    )
    assert is_subset_dict(
        {"result": False, "value": -1.0, "reason": "number is not positive"}, calculate({"number": -1.0}, "number")
    )
