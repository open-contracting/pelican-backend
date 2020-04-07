import csv

from tools.checks import get_empty_result_field

ocid_prefixes = None
name = 'ocid_prefix_check'


def calculate(data, key):
    result = get_empty_result_field(name)

    if ocid_prefixes is None:
        initialise_ocid_prefixes()

    if key not in data:
        result['result'] = False
        result['value'] = None
        result['reason'] = 'missing key'
        return result

    ocid = data[key]
    if type(ocid) != str or not ocid:
        result['result'] = False
        result['value'] = ocid
        result['reason'] = 'wrong ocid'
        return result

    for correct_ocid in ocid_prefixes:
        if ocid.startswith(correct_ocid):
            result['result'] = True
            return result

    result['result'] = False
    result['value'] = ocid
    result['reason'] = 'wrong ocid'
    return result


def initialise_ocid_prefixes():
    global ocid_prefixes
    ocid_prefixes = []

    with open('registry/ocid_prefixes.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            ocid_prefixes.append(row['OCID'])
