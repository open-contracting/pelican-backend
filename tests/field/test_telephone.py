from contracting_process.field_level.checks.telephone import calculate
from tests import is_subset_dict

"""
author: Iaroslav Kolodka

The file contain tests for a function contracting_process.field_level.telephone.telephone_number_format .

'test_with_correct_number' is the case when the input item contains a correctly formatted phone number.
'test_with_incorrect_number' is the case when the input item contains an incorrectly formatted phone number.


"""

item_with_valid_number1 = {"telephone": "+420777555333"}

item_with_invalid_number1 = {"telephone": "+42077755533"}

item_with_invalid_number2 = {"telephone": "+420777555a33"}

item_with_invalid_number3 = {"telephone": "+999777555333"}


def test_with_correct_number():
    expected_result = {"result": True}
    result1 = calculate(item_with_valid_number1, "telephone")
    assert is_subset_dict(expected_result, result1)


def test_with_incorrect_number():
    expected_result1 = {
        "result": False,
        "value": "+42077755533",  # number is too short
        "reason": "Telephone number is formatted incorrectly.",
    }
    expected_result2 = {
        "result": False,
        "value": "+420777555a33",  # incorrect number
        "reason": "Telephone number is formatted incorrectly.",
    }
    expected_result3 = {
        "result": False,
        "value": "+999777555333",  # the region shuld not exist
        "reason": "Telephone number is formatted incorrectly.",
    }
    result1 = calculate(item_with_invalid_number1, "telephone")
    result2 = calculate(item_with_invalid_number2, "telephone")
    result3 = calculate(item_with_invalid_number3, "telephone")
    assert is_subset_dict(expected_result1, result1)
    assert is_subset_dict(expected_result2, result2)
    assert is_subset_dict(expected_result3, result3)
