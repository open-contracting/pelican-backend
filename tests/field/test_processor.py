import pytest

from contracting_process.processor import field_level_checks
from tests import read


# https://requests-cache.readthedocs.io/en/stable/user_guide/troubleshooting.html#common-error-messages
@pytest.mark.filterwarnings("ignore:unclosed <ssl.SSLSocket fd=:ResourceWarning")
def test_field_level_checks():
    row = field_level_checks(read("compiled-release"), 123, 1)
    result = row["result"].obj

    assert result == read("field-result")
    assert row["data_item_id"] == 123
    assert row["dataset_id"] == 1


def test_field_level_checks_invalid():
    row = field_level_checks({"ocid": "1", "tender": {"tenderers": "string"}}, 123, 1)
    result = row["result"].obj

    assert "tender.tenderers.contactPoint.name" not in result["checks"]
    assert result["checks"]["tender.tenderers.contactPoint"] == [
        {
            "coverage": {
                "check_results": [
                    {
                        "name": "exists",
                        "reason": "parent is a str, not an object",
                        "result": False,
                        "value": "string",
                        "version": 1.0,
                    }
                ],
                "overall_result": False,
            },
            "path": "tender.tenderers.contactPoint",
            "quality": {"check_results": [], "overall_result": None},
        }
    ]
    assert row["data_item_id"] == 123
    assert row["dataset_id"] == 1
