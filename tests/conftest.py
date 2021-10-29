import json
import os

import pytest
from jsonschema import FormatChecker


@pytest.fixture(scope="session")
def schema():
    # From standard-maintenance-scripts/tests/test_readme.py
    def set_additional_properties_false(data):
        if isinstance(data, list):
            for item in data:
                set_additional_properties_false(item)
        elif isinstance(data, dict):
            if "properties" in data:
                data["additionalProperties"] = False
            for value in data.values():
                set_additional_properties_false(value)

    with open(os.path.join("tests", "fixtures", "release-schema.json")) as f:
        schema = json.load(f)

    set_additional_properties_false(schema)

    return schema


@pytest.fixture(scope="session")
def format_checker():
    return FormatChecker()
