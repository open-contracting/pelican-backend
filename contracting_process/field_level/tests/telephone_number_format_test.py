from contracting_process.field_level.telephone import telephone_number_format
from functools import partial

"""
author: Iaroslav Kolodka

The file contain tests for a function contracting_process.field_level.telephone.telephone_number_format .

'test_with_correct_number' is the case when the input item contains a correctly formatted phone number.
'test_with_incorrect_number' is the case when the input item contains an incorrectly formatted phone number.


"""

telephone_number_format_prepared = partial(
    telephone_number_format,
    key="telephone",
    default_region="CZ"
)

item_with_valid_number1 = {
    "telephone": "+420777555333"
}

item_with_valid_number2 = {
    "telephone": "420777555333"
}

item_with_valid_number3 = {
    "telephone": "777555333"
}

item_with_invalid_number1 = {
    "telephone": "+42077755533"
}

item_with_invalid_number2 = {
    "telephone": "+420777555a33"
}

item_with_invalid_number3 = {
    "telephone": "+999777555333"
}


def test_with_correct_number():
    expected_result = {
        "result": True
    }
    result1 = telephone_number_format_prepared(item_with_valid_number1)
    result2 = telephone_number_format_prepared(item_with_valid_number2)
    result3 = telephone_number_format_prepared(item_with_valid_number3)
    assert result1 == expected_result
    assert result2 == expected_result
    assert result3 == expected_result


def test_with_incorrect_number():
    expected_result1 = {
        "result": False,
        "value": "+42077755533",  # number is too short
        "reason": "Telephone number is formatted incorrectly or does not exist"
    }
    expected_result2 = {
        "result": False,
        "value": "+420777555a33",  # incorrect number
        "reason": "Telephone number is formatted incorrectly or does not exist"
    }
    expected_result3 = {
        "result": False,
        "value": "+999777555333",  # the region shuld not exist
        "reason": "Telephone number is formatted incorrectly or does not exist"
    }
    result1 = telephone_number_format_prepared(item_with_invalid_number1)
    result2 = telephone_number_format_prepared(item_with_invalid_number2)
    result3 = telephone_number_format_prepared(item_with_invalid_number3)
    assert result1 == expected_result1
    assert result2 == expected_result2
    assert result3 == expected_result3
