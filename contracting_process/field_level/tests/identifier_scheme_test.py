from contracting_process.field_level.identifier_scheme import identifier_scheme_codelist_checker

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
    expected_result = {"result": True}
    assert identifier_scheme_codelist_checker(item, "identifier") == expected_result


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
    expected_result = {
        "result": False,
        "value": None,
        "reason": "Value is not from org-id.guide"
    }
    assert identifier_scheme_codelist_checker(item_without_properties, "identifier") == expected_result
    assert identifier_scheme_codelist_checker(item_without_scheme, "identifier") == expected_result
    expected_result["value"] = "XI-PB-WWW"
    assert identifier_scheme_codelist_checker(item_with_invalid_scheme_value, "identifier") == expected_result
