import os
from unittest.mock import patch

import pytest

from dataset.misc import url_availability

item_unset = {"ocid": "0"}
item_test_undefined = {"ocid": "0", "planning": {"documents": [{"url": "https://postman-echo.com/status/200"}]}}


class mock_settings:
    REQUESTS_TIMEOUT = 1


def test_undefined():
    scope = {}
    scope = url_availability.add_item(scope, item_unset, 0)
    result = url_availability.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}

    scope = {}
    scope = url_availability.add_item(scope, item_test_undefined, 0)
    result = url_availability.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "fewer than 100 occurrences of necessary fields"}


item_test_passed = {
    "ocid": "0",
    "planning": {"documents": [{"url": "https://postman-echo.com/status/200"} for _ in range(25)]},
    "tender": {"documents": [{"url": "https://postman-echo.com/status/200"} for _ in range(25)]},
    "awards": [{"documents": [{"url": "https://postman-echo.com/status/200"}]} for _ in range(25)],
    "contracts": [{"documents": [{"url": "https://postman-echo.com/status/200"}]} for _ in range(25)],
}


@pytest.mark.skipif("CI" not in os.environ, reason="skipping slow test in development")
def test_passed():
    scope = {}
    scope = url_availability.add_item(scope, item_test_passed, 0)
    result = url_availability.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert len(result["meta"]["passed_examples"]) == 100
    assert len(result["meta"]["failed_examples"]) == 0
    assert all(example["status"] == "OK" for example in result["meta"]["passed_examples"])


items_test_failed_multiple = [
    {"ocid": str(num), "planning": {"documents": [{"url": "https://postman-echo.com/status/200"}]}}
    for num in range(99)
]
items_test_failed_multiple.append(
    {"ocid": "99", "planning": {"documents": [{"url": "https://postman-echo.com/delay/10"}]}}
)


@pytest.mark.skipif("CI" not in os.environ, reason="skipping slow test in development")
def test_failed_multiple():
    with patch.object(url_availability, "settings", new=mock_settings):
        scope = {}

        item_id = 0
        for item in items_test_failed_multiple:
            scope = url_availability.add_item(scope, item, item_id)
            item_id += 1

        result = url_availability.get_result(scope)
        assert result["result"] is False
        assert result["value"] >= 95
        assert len(result["meta"]["passed_examples"]) >= 95
        assert len(result["meta"]["failed_examples"]) <= 5
        assert sum(1 for example in result["meta"]["passed_examples"] if example["status"] == "OK") >= 95
        assert sum(1 for example in result["meta"]["failed_examples"] if example["status"] != "OK") <= 5
