from tools.getter import get_values
import phonenumbers

"""
author: Iaroslav Kolodka

The method is designed to check the telephone number for the correct formatting

parametres:
    - item: tested JSON
    - path: path to tуlephone number
    - default_region: default region in case the phone number does not have it

"""


def telephone_number_format(item, path, default_region):
    numbers = get_values(item, path, True)
    value = None
    if numbers:
        value = numbers[0]
        try:
            parsed_number = phonenumbers.parse(value, default_region)
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
