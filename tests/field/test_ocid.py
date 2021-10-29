from contracting_process.field_level.format.ocid import calculate
from tests import is_subset_dict


def test_passed():
    assert is_subset_dict({"result": True}, calculate({"ocid": "ocds-a2ef3d"}, "ocid"))
    assert is_subset_dict({"result": True}, calculate({"ocid": "ocds-a2ef3d123123123"}, "ocid"))


def test_failed():
    assert is_subset_dict(
        {"result": False, "value": "a000-a00000", "reason": "wrong ocid"},
        calculate({"ocid": "a000-a00000"}, "ocid"),
    )
