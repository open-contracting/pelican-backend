import csv

from settings import settings
from tools.checks import get_empty_result_field

format_codelist = None
name = "document_format_codelist"


def calculate(item, key):
    result = get_empty_result_field(name)
    result["result"] = False

    if format_codelist is None:
        initialise_format_codelist()

    document_format = item[key]

    passed = document_format in format_codelist
    result["result"] = passed

    if not passed:
        result["value"] = document_format
        result["reason"] = "wrong document format"

    return result


def initialise_format_codelist():
    global format_codelist
    format_codelist = []

    with open("registry/format_codelist.csv", "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            format_codelist.append(row["Template"])

    format_codelist.extend(settings.ADDITIONAL_DOCUMENT_FORMATS)
