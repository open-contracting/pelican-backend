from contracting_process.field_level.checks.email import calculate
from tools.helpers import is_subset_dict

"""
author: Iaroslav Kolodka

The file contain tests for a function contracting_process.field_level.email.emaill_format.

'test_with_correct_email' is the case when the input item contains correctly formatted email.
'test_with_incorrect_email' is the case when the input item contains an incorrectly formatted email.


"""

item_with_valid_email = {"email": "valid@gmail.com"}

item_with_invalid_email = {"email": "invalid#email.com"}


def test_with_correct_email():
    result = calculate(item_with_valid_email, "email")
    assert is_subset_dict({"result": True}, result)


def test_with_incorrect_email():
    result = calculate(item_with_invalid_email, "email")
    assert is_subset_dict({"result": False, "value": "invalid#email.com", "reason": "Incorrect email format"}, result)
