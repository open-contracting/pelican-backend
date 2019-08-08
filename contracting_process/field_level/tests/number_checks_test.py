from contracting_process.field_level.number_checks import positive_number


def test_positive_number():
    assert positive_number({"number": 10}, "number") == {"result": True}
    assert positive_number({}, "number") == {
        "result": False,
        "value": None,
        "reason": "missing key"
    }
    assert positive_number({"name_of_value": 10}, "number") == {
        "result": False,
        "value": None,
        "reason": "missing key"
    }
    assert positive_number({"name_of_value": "value"}, "number") == {
        "result": False,
        "value": None,
        "reason": "missing key"
    }
    assert positive_number({"number": "value"}, "number") == {
        "result": False,
        "value": "value",
        "reason": "not a number"
    }
    assert positive_number({"number": 10.0}, "number") == {"result": True}
    assert positive_number({"number": 10j}, "number") == {
        "result": False,
        "value": 10j,
        "reason": "not a number"
    }
    assert positive_number({"number": 0}, "number") == {
        "result": False,
        "value": 0,
        "reason": "number is not positive"
    }
    assert positive_number({"number": -1}, "number") == {
        "result": False,
        "value": -1,
        "reason": "number is not positive"
    }
