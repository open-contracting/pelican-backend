import csv

global_OCIDs = []


def right_ocid_format(data, key):
    if key not in data:
        return {"result": False,
                "value": None,
                "reason": "missing key"}

    ocid = data[key]
    if type(ocid) != str or not ocid:
        return {"result": False,
                "value": ocid,
                "reason": "wrong ocid"}

    if bool(global_OCIDs) is False:
        initialise_global_OCIDs()

    for correct_ocid in global_OCIDs:
        if ocid.startswith(correct_ocid):
            return {"result": True}

    return {"result": False,
            "value": ocid,
            "reason": "wrong ocid"}


def initialise_global_OCIDs():
    path = 'contracting_process/field_level/OCID_prefixes.csv'

    OCIDs_file = open(path, "r")
    reader = csv.reader(OCIDs_file)
    for line in reader:
        global_OCIDs.append(line[0])
