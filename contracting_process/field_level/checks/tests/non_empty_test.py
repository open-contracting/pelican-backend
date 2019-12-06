from contracting_process.field_level.checks.non_empty import calculate
from tools.helpers import is_subset_dict


def test_non_empty():
    assert is_subset_dict(
        {"result": True},
        calculate({"amount": 0}, "amount")
    )
    assert is_subset_dict(
        {"result": True},
        calculate({"lang": "en"}, "lang")
    )
    assert is_subset_dict(
        {"result": False, "value": "", "reason": "empty string"},
        calculate({"lang": ""}, "lang")
    )
    assert is_subset_dict(
        {"result": False, "value": [], "reason": "empty list"},
        calculate({"lang": []}, "lang")
    )
    assert is_subset_dict(
        {"result": False, "value": {}, "reason": "empty dictionary"},
        calculate({"lang": {}}, "lang")
    )
    assert is_subset_dict(
        {"result": False, "value": None, "reason": "missing key"},
        calculate({"lang": {}}, "lang2")
    )
