from tools.getter import get_values
from validate_email import validate_email

"""
author: Iaroslav Kolodka

The method is designed to check the email address for the correct formatting.

parametre:
    - item: tested JSON
    - key:  email key

"""


def email_format(item, key):
    email = item[key]
    value = None
    if email:
        value = email
        is_valid = validate_email(value)
        if is_valid:
            return {
                "result": True
            }
    return{
        "result": False,
        "value": value,
        "reason": "Email is formatted incorrectly or does not exist"
    }
