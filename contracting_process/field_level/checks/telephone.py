import phonenumbers
from tools.getter import get_values
from tools.checks import get_empty_result_field

"""
author: Iaroslav Kolodka

"""
name = "telephone"


def calculate(item, key):
    """
    The method is designed to check the telephone number for the correct formatting

    parametres
    ---------
    :item : JSON
            tested JSON
    :path : str
            path to tуlephone number

    """
    result = get_empty_result_field(name)

    number = item[key]
    value = None
    if number:
        value = number
        try:
            parsed_number = phonenumbers.parse(value, None)
            is_valid = phonenumbers.is_possible_number(parsed_number)
            if is_valid:
                result["result"] = True
                return result

        except phonenumbers.NumberParseException:
            pass

    result["result"] = False
    result["value"] = value
    result["reason"] = "Telephone number is formatted incorrectly."
    return result
