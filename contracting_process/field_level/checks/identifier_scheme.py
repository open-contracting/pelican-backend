
import csv

from tools.checks import get_empty_result_field
from tools.getter import get_values

"""
author: Iaroslav Kolodka

"""

"""
A global list containing 'contracting_process/field_level/checks/identifier_scheme_codelist.csv' .

"""
global_identifier_scheme_codelist = []
name = "identifier_scheme"


def calculate(item, key):
    result = get_empty_result_field(name)

    if item and "scheme" in item:
        scheme_type = item["scheme"]
        if scheme_type and type(scheme_type) == str:
            if not global_identifier_scheme_codelist:
                initialise_global_identifier_scheme_codelist()
            if scheme_type in global_identifier_scheme_codelist:
                result["result"] = True
            else:
                result["result"] = False
                result["value"] = scheme_type
                result["reason"] = "Value is not from org-id.guide"
    return result


def initialise_global_identifier_scheme_codelist():
    path = "contracting_process/field_level/checks/identifier_scheme_codelist.csv"

    first = 0  # means 'first colun'
    file = open(path, "r")
    codelist = csv.reader(file)
    for line in codelist:
        global_identifier_scheme_codelist.append(line[first])
