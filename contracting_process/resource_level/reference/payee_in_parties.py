from contracting_process.resource_level.reference.lib import \
    calculate_reference_in_parties
from tools.getter import get_values

version = 1.0


def calculate(item):
    """Checks whether the item.contracts.implementation.transactions.payee are all referenced in the item.parties array.

    Args:
        item: item to be checked
    """
    values = get_values(item, "contracts.implementation.transactions.payee")
    return calculate_reference_in_parties(item, values, version)
