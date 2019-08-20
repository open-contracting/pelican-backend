from tools.getter import get_values
import phonenumbers

"""
author: Iaroslav Kolodka

"""


def telephone_number_format(item, key):
    """
    The method is designed to check the telephone number for the correct formatting

    parametres
    ---------
    :item : JSON
            tested JSON
    :path : str
            path to tуlephone number

    """
    number = item[key]
    value = None
    if number:
        value = number
        try:
            parsed_number = phonenumbers.parse(value, None)
            is_valid = phonenumbers.is_possible_number(parsed_number)
            if is_valid:
                return {
                    "result": True
                }
        except phonenumbers.NumberParseException:
            pass
    return{
        "result": False,
        "value": value,
        "reason": "Telephone number is formatted incorrectly or does not exist"
    }
