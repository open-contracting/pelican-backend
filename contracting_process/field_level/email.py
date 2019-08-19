from tools.getter import get_values
from validate_email import validate_email

"""
author: Iaroslav Kolodka

Method is designed to check email address on correct formatting

parametr:
    - item: tested JSON
    - path: path to email

"""


def email_format(item, path):
    email = get_values(item, path, True)
    is_valid = validate_email(email[0], verify=True)
    if is_valid:
        return {
            "result": True
        }
    else:
        return{
            "result": False,
            "value": email[0],
            "reason": "Email has incorrect formatting or doesn`t exists"
        }
