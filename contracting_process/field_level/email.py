from tools.getter import get_values
from validate_email import validate_email

"""
author: Iaroslav Kolodka

The method is designed to check the email address for the correct formatting
and existence (in case formatting is correct).

parametre:
    - item: tested JSON
    - path: path to email

"""


def email_format(item, path):
    email = get_values(item, path, True)
    value = None
    if email:
        value = email[0]
        is_valid = validate_email(value, verify=True)
        if is_valid:
            return {
                "result": True
            }
    return{
        "result": False,
        "value": value,
        "reason": "Email is formatted incorrectly or does not exist"
    }
