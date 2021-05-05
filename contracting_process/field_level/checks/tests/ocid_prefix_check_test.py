import contracting_process.field_level.checks.ocid_prefix_check as ocid_prefix_check
from tools.helpers import is_subset_dict


def test_passed():
    ocid_prefix_check.ocid_prefixes = ["ocds-a2e", "ocds-a2ef3d123123123"]

    assert is_subset_dict({"result": True}, ocid_prefix_check.calculate({"ocid": "ocds-a2ef3d"}, "ocid"))
    assert is_subset_dict({"result": True}, ocid_prefix_check.calculate({"ocid": "ocds-a2ef3d123123123"}, "ocid"))


def test_failed():
    ocid_prefix_check.ocid_prefixes = []

    assert is_subset_dict(
        {"result": False, "value": "a000-a00000", "reason": "wrong ocid"},
        ocid_prefix_check.calculate({"ocid": "a000-a00000"}, "ocid"),
    )
