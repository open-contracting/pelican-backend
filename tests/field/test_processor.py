import json

from contracting_process.processor import field_level_checks
from tests import read


def test_field_level_checks():
    string, item_id, dataset_id = field_level_checks(read("compiled-release"), 123, 1)

    assert json.loads(string) == read("field-result")
    assert item_id == 123
    assert dataset_id == 1
