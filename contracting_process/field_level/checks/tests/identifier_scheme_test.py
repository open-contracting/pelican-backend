
from contracting_process.field_level.checks.identifier_scheme import calculate
from tools.helpers import is_subset_dict

"""
author: Iarosav Kolodka

The file contains tests for function
'contracting_process.field_level.identifier_scheme.identifier_scheme_codelist_checker' .

'test_valid_value' test with valid data
'test_invalid_values' test with invalid data:
    - identifier has not 'properties'
    - identifier has not 'scheme'
    - identifier ivalid scheme type

"""


def test_valid_value():
    item = {
        "identifier": {
            "scheme": "XI-PB"
        }
    }
    assert is_subset_dict(
        {"result": True},
        calculate(item, "identifier")
    )


def test_invalid_values():
    item_without_properties = {
        "identifier": {
        }
    }
    item_without_scheme = {
        "identifier": {
        }
    }
    item_with_invalid_scheme_value = {
        "identifier": {
            "scheme": "XI-PB-WWW"
        }
    }

    assert is_subset_dict(
        {
            "result": False,
            "value": None,
            "reason": "Value is not from org-id.guide"
        },
        calculate(item_without_properties, "identifier")
    )
    assert is_subset_dict(
        {
            "result": False,
            "value": None,
            "reason": "Value is not from org-id.guide"
        },
        calculate(item_without_scheme, "identifier")
    )
    assert is_subset_dict(
        {
            "result": False,
            "value": "XI-PB-WWW",
            "reason": "Value is not from org-id.guide"
        },
        calculate(item_with_invalid_scheme_value, "identifier")
    )
