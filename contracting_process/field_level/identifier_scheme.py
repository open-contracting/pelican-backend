
import csv

from tools.checks import get_empty_result_field
from tools.getter import get_values

"""
author: Iaroslav Kolodka

"""

"""
A global list containing 'contracting_process/field_level/identifier_scheme_codelist.csv' .

"""
global_identifier_scheme_codelist = []
name = "identifier_scheme"


def calculate(item, key: str) -> dict:
    """ The fumction checks 'schema' in '$ref: "#/definitions/Identifier"' object from 'OCDS schema'.

    The value must be from 'org-id.guide'. The codelist is placed under the name: 'identifier_scheme_codelist.csv'
    in CSV file. The first use of a check fills 'global_identifier_scheme_codelist'

    parametres
    ----------
    item : dict
        tested JSON
    key : str
        key to value

    returns
    ----------
    type: dict
        success case: {"result": True}
        failed case: {
            "result": False,
            "value": information contains in 'scheme',
            "reason": "Value is not from org-id.guide"
        }

    """
    result = get_empty_result_field(name)

    scheme_type = None
    identifier = item[key]
    if identifier and "scheme" in identifier:
            scheme_type = identifier["scheme"]
            if scheme_type and type(scheme_type) == str:
                if not global_identifier_scheme_codelist:
                    initialise_global_identifier_scheme_codelist()
                if scheme_type in global_identifier_scheme_codelist:
                    result["result"] = True
                    return result

    result["result"] = False
    result["value"] = scheme_type
    result["reason"] = "Value is not from org-id.guide"
    return result


def initialise_global_identifier_scheme_codelist():
    """ The function fills global dictionary 'global_identifier_scheme_codelist' .

    The function uses identifier_scheme_codelist.csv .

    parmetres
    ---------
    None

    return
    ---------
    None

    """
    path = "contracting_process/field_level/identifier_scheme_codelist.csv"

    first = 0  # means 'first colun'
    file = open(path, "r")
    codelist = csv.reader(file)
    for line in codelist:
        global_identifier_scheme_codelist.append(line[first])
