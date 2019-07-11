from contracting_process.resource_level.reference.lib import \
    calculate_reference_in_parties
from tools.getter import get_values

version = 1.0


def calculate(item):
    values = get_values(item, "tender.tenderers")
    return calculate_reference_in_parties(item, values, version)
