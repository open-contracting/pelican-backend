import csv
from tools.checks import get_empty_result_field

global_format_codelist = []
name = "document_format_codelist"


def calculate(data, key):
    result = get_empty_result_field(name)
    result["result"] = False

    if key in data:
        file_format = data[key]
        if file_format and type(file_format) is str:
            if not global_format_codelist:
                initialise_global_format_codelist()

            if file_format in global_format_codelist or file_format == "offline/print":
                result["result"] = True
            else:
                result["result"] = False
                result["value"] = file_format
                result["reason"] = "wrong file format"

    return result


def initialise_global_format_codelist():
    path = 'contracting_process/field_level/checks/format_codelist.csv'

    file = open(path, "r")
    reader = csv.reader(file)
    for line in reader:
        global_format_codelist.append(line[0])
