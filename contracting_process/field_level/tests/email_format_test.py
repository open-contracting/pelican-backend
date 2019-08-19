from contracting_process.field_level.email import email_format
from functools import partial
email_format_prepared = partial(
    email_format,
    path="parties.contactPoint.email"
)

item_with_correct_email = {
    "parties": [
        {
            "contactPoint": {
                "email": "yaroslav.kolodka@gmail.com"
            }
        }
    ]
}

item_with_incorrect_email = {
    "parties": [
        {
            "contactPoint": {
                "email": "email#google.com"
            }
        }
    ]
}


item_with_correct_email_which_does_not_exist = {
    "parties": [
        {
            "contactPoint": {
                "email": "email.does.not@exist.com.com.com"
            }
        }
    ]
}


def test_with_correct_email():
    expcted_result = {
        "result": True
    }
    result = email_format_prepared(item_with_correct_email)
    assert result == expcted_result


def test_with_incorrect_email():
    expcted_result = {
        "result": False,
        "value": "email#google.com",
        "reason": "Email has incorrect formatting or doesn`t exists"
    }
    result = email_format_prepared(item_with_incorrect_email)
    assert result == expcted_result


def test_with_correct_email_which_does_not_exist():
    expcted_result = {
        "result": False,
        "value": "email.does.not@exist.com.com.com",
        "reason": "Email has incorrect formatting or doesn`t exists"
    }
    result = email_format_prepared(item_with_correct_email_which_does_not_exist)
    assert result == expcted_result
