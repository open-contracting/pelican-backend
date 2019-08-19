from contracting_process.field_level.email import email_format
from functools import partial

"""
author: Iaroslav Kolodka

The file contain tests for a function contracting_process.field_level.email.emaill_format.

'test_with_correct_email' is the case when the input item contains an existing correctly formatted email.
'test_with_incorrect_email' is the case when the input item contains an incorrectly formatted email.
'test_with_correct_email_which_does_not_exist' is the case when the input item contains a non-existing correctly
 formatted email.


"""

item_with_valid_email = {
    "email": "yaroslav.kolodka@gmail.com"
}

item_with_invalid_email = {
    "email": "email#google.com"
}


item_with_valid_email_which_does_not_exist = {
    "email": "agdshfgasdhgfsjdhfgasjkdhgfaskjfgahsdfg@gmail.com"
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
        "value": "email#google.com",
        "reason": "Email is formatted incorrectly or does not exist"
    }
    result = email_format(item_with_invalid_email, "email")
    assert result == expected_result


def test_with_correct_email_which_does_not_exist():
    expected_result = {
        "result": False,
        "value": "agdshfgasdhgfsjdhfgasjkdhgfaskjfgahsdfg@gmail.com",  # there must be a definitely non-existent email
        "reason": "Email is formatted incorrectly or does not exist"
    }
    result = email_format(item_with_valid_email_which_does_not_exist, "email")
    assert result == expected_result
