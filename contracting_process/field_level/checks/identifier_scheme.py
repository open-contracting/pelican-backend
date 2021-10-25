import csv

from tools.checks import get_empty_result_field

identifier_scheme_codelist = None
name = "identifier_scheme"


def calculate(item, key):
    result = get_empty_result_field(name)

    if identifier_scheme_codelist is None:
        initialise_identifier_scheme_codelist()

    scheme = item[key]

    passed = scheme in identifier_scheme_codelist
    result["result"] = passed

    if not passed:
        result["value"] = scheme
        result["reason"] = "wrong identifier scheme"

    return result


def initialise_identifier_scheme_codelist():
    global identifier_scheme_codelist
    identifier_scheme_codelist = []

    with open("registry/identifier_scheme_codelist.csv", "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            identifier_scheme_codelist.append(row["code"])
