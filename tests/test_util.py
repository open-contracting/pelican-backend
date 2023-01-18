from tests import is_subset_dict


def test_is_subset_dict():
    assert is_subset_dict({}, {"a": 1}) is True
    assert is_subset_dict({"a": 1}, {"a": 1}) is True
    assert is_subset_dict({"a": 1}, {"a": 1, "b": 2}) is True
    assert is_subset_dict({"a": 0}, {"a": 1}) is False
    assert is_subset_dict({"a": 1, "b": 2}, {"a": 1}) is False
