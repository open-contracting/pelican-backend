
import csv

"""
author: Iaroslav Kolodka

"""

global_format_codelist = []


def document_format_codelist(data, key):
    """ The check function for document format.

    The function uses format_list.csv whisch is stored in 'global_format_codelist'

    Parameters
    ----------
    data : tested JSON
    key : test data key

    Returns
    ----------
    None

    """
    document = data[key]
    file_format = None
    if "format" in document:
        file_format = document["format"]
        if file_format or type(file_format) is str:

            if bool(global_format_codelist) is False:
                initialise_global_format_codelist()

            for valid_file_format in global_format_codelist:
                if file_format == valid_file_format:
                    return {"result": True}

    return {"result": False,
            "value": file_format,
            "reason": "wrong file format"}


def initialise_global_format_codelist():
    """ The function initialising 'global_format_codelist'.

    The function use format_list.csv to initialise global variable

    Parameters
    ----------
    None

    Returns
    ----------
    None

    """
    path = 'contracting_process/field_level/format_codelist.csv'

    file = open(path, "r")
    reader = csv.reader(file)
    for line in reader:
        global_format_codelist.append(line[0])
