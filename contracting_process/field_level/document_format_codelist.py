
import csv

"""
    author: Iaroslav Kolodka

"""

"""
    The list contains list of codes from: 'contracting_process/field_level/format_codelist.csv'.
"""

global_format_codelist = []


def document_format_codelist(data, key: str) -> dict:
    """ The check function for document format.

        The function uses format_list.csv whisch is stored in 'global_format_codelist'

        Parametres
        ----------
        data : dict
            tested JSON
        key : str
            test data key

        Returns
        ----------
        '' : dict
            -   { "result": True }
            -   {
                    "result": False,
                    "value": file_format,
                    "reason": "wrong file format"
                }
            -   {
                    "result": False,
                    "value": file_format,
                    "reason": "wrong file format"
                }

    """
    documents = data[key]
    file_format = None
    for document in documents:
        if "format" in document:
            file_format = document["format"]
            if file_format and type(file_format) is str:

                if not global_format_codelist:
                    initialise_global_format_codelist()

                if file_format in global_format_codelist:
                    continue
                if file_format == "offline/print":
                    continue

            return {
                "result": False,
                "value": file_format,
                "reason": "wrong file format"
            }
        else:
            return {
                "result": None,
                "value": None,
                "reason": "Document has no format"
            }
    return {
        "result": True
    }


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
