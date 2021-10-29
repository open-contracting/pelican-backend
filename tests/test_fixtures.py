import os
import warnings

import pytest
from jsonschema.validators import Draft4Validator as validator


def custom_warning_formatter(message, category, filename, lineno, line=None):
    return str(message).replace(os.getcwd() + os.sep, "")


warnings.formatwarning = custom_warning_formatter


def get_test_cases():
    excluded_files = {"test_fixtures.py", "test_converter.py"}

    for root, dirs, files in os.walk("tests"):
        for directory in list(dirs):
            # Field-level tests use sub-schema, not the release schema.
            if directory.startswith("__") or directory == "field":  # __pycache__
                dirs.remove(directory)

        for file in files:
            if not file.startswith("test_") or not file.endswith(".py") or file in excluded_files:
                continue

            filename = os.path.join(root, file)

            # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
            import importlib.util

            spec = importlib.util.spec_from_file_location("dummy", filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for key, value in module.__dict__.items():
                if key.startswith("__"):
                    continue
                if isinstance(value, (dict, list)):
                    yield filename, key, value


def add_id(value, *keys):
    for key in keys:
        if key in value:
            for i, item in enumerate(value[key]):
                item.setdefault("id", str(i))


@pytest.mark.parametrize("filename,key,values", list(get_test_cases()))
def test_valid(filename, key, values, schema, format_checker):
    errors = 0

    invalid = key.endswith("__invalid_schema")

    if not isinstance(values, list):
        values = [values]

    for value in values:
        if not isinstance(value, dict):
            continue

        # Add required fields.
        value.setdefault("ocid", "ocid")
        value.setdefault("id", "id")
        value.setdefault("date", "2000-01-01T00:00:00Z")
        value.setdefault("tag", ["tender"])
        value.setdefault("initiationType", "tender")

        if "planning" in value:
            add_id(value["planning"], "documents", "milestones")
        if "tender" in value:
            value["tender"].setdefault("id", "id")
            add_id(value["tender"], "documents", "items", "milestones")
        if "awards" in value:
            for i, item in enumerate(value["awards"]):
                item.setdefault("id", str(i))
                add_id(item, "documents")
        if "contracts" in value:
            for i, item in enumerate(value["contracts"]):
                item.setdefault("id", str(i))
                item.setdefault("awardID", str(i))
                add_id(item, "documents", "milestones")
                if "implementation" in item:
                    add_id(item["implementation"], "documents", "milestones", "transactions")

        # Validate the item.
        for error in validator(schema, format_checker=format_checker).iter_errors(value):
            errors += 1
            # warnings.warn(json.dumps(error.instance, indent=2))
            if not invalid:
                warnings.warn(f"{key} {error.message} ({'/'.join(error.absolute_schema_path)})\n")

    if invalid:
        assert errors, f"{filename}:{key} is valid, but is expected to be invalid"
    else:
        assert errors == 0, f"{filename}:{key} is invalid. See warnings below."
