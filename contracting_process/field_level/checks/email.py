
from tools.checks import get_empty_result_field
from tools.getter import get_values
from validate_email import validate_email

"""
author: Iaroslav Kolodka

The method is designed to check the email address for the correct formatting.

parametre:
    - item: tested JSON
    - key:  email key

"""
name = "email"


def calculate(item, key):
    result = get_empty_result_field(name)

    email = item[key]
    value = None
    if email:
        value = email
        is_valid = validate_email(value)
        if is_valid:
            result["result"] = True
            return result

    result["result"] = False
    result["value"] = value
    result["reason"] = "Incorrect email format"
    return result
