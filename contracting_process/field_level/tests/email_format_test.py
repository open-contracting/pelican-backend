from contracting_process.field_level.email import email_format

"""
author: Iaroslav Kolodka

The file contain tests for a function contracting_process.field_level.email.emaill_format.

'test_with_correct_email' is the case when the input item contains correctly formatted email.
'test_with_incorrect_email' is the case when the input item contains an incorrectly formatted email.


"""

item_with_valid_email = {
    "email": "valid@gmail.com"
}

item_with_invalid_email = {
    "email": "invalid#email.com"
}


def test_with_correct_email():
    expected_result = {
        "result": True
    }
    result = email_format(item_with_valid_email, "email")
    assert result == expected_result


def test_with_incorrect_email():
    expected_result = {
        "result": False,
        "value": "invalid#email.com",
        "reason": "Email is formatted incorrectly or does not exist"
    }
    result = email_format(item_with_invalid_email, "email")
    assert result == expected_result
