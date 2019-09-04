
from contracting_process.field_level.checks.ocid_prefix_check import calculate
from tools.helpers import is_subset_dict


def test_ocid_prefix_ok():
    assert is_subset_dict(
        {"result": True},
        calculate({"ocid": "ocds-a2ef3d"}, "ocid")
    )
    assert is_subset_dict(
        {"result": True},
        calculate({"ocid": "ocds-a2ef3d123123123"}, "ocid")
    )


def test_ocid_prefix_failed():
    assert is_subset_dict(
        {"result": False, "value": "a000-a00000", "reason": "wrong ocid"},
        calculate({"ocid": "a000-a00000"}, "ocid")
    )
    assert is_subset_dict(
        {"result": False, "value": 123123, "reason": "wrong ocid"},
        calculate({"ocid": 123123}, "ocid")
    )
    assert is_subset_dict(
        {"result": False, "value": None, "reason": "missing key"},
        calculate({}, "ocid")
    )
    assert is_subset_dict(
        {"result": False, "value": "", "reason": "wrong ocid"},
        calculate({"ocid": ""}, "ocid")
    )
