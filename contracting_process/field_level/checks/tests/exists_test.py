from contracting_process.field_level.checks.exists import calculate
from tools.helpers import is_subset_dict


def test_exists():
    assert is_subset_dict({"result": True}, calculate({"lang": "en"}, "lang"))
    assert is_subset_dict({"result": True}, calculate({""}, ""))
    assert is_subset_dict(
        {"result": False, "value": None, "reason": "missing key"}, calculate({"lang": "en"}, "lang2")
    )
    assert is_subset_dict({"result": False, "value": None, "reason": "missing key"}, calculate({}, "lang2"))
    assert is_subset_dict({"result": False, "value": None, "reason": "missing key"}, calculate({}, ""))
