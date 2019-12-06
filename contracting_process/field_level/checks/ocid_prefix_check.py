import csv

from tools.checks import get_empty_result_field

global_OCIDs = []
name = "ocid_prefix_check"


def calculate(data, key):
    result = get_empty_result_field(name)

    if key not in data:
        result["result"] = False
        result["value"] = None
        result["reason"] = "missing key"
        return result

    ocid = data[key]
    if type(ocid) != str or not ocid:
        result["result"] = False
        result["value"] = ocid
        result["reason"] = "wrong ocid"
        return result

    if bool(global_OCIDs) is False:
        initialise_global_OCIDs()

    for correct_ocid in global_OCIDs:
        if ocid.startswith(correct_ocid):
            result["result"] = True
            return result

    result["result"] = False
    result["value"] = ocid
    result["reason"] = "wrong ocid"
    return result


def initialise_global_OCIDs():
    path = 'contracting_process/field_level/checks/OCID_prefixes.csv'

    OCIDs_file = open(path, "r")
    reader = csv.reader(OCIDs_file)
    for line in reader:
        global_OCIDs.append(line[0])
