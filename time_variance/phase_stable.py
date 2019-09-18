import random

from tools.checks import get_empty_result_time_variance
from tools.getter import get_values

version = 1.0


def filter(scope, item, item_id, new_item, new_item_id):
    # entry filtering - check makes sense only for tenders with a title filled in
    if item:
        return True


def evaulate(scope, item, item_id, new_item, new_item_id):
    result = True

    ancestor_values = get_values(item, "tender", value_only=True)
    if ancestor_values and len(ancestor_values[0]) > 0:
        new_values = get_values(new_item, "tender", value_only=True)
        if not new_values or len(new_values[0]) < 1:
            return scope, False

    ancestor_values = get_values(item, "planning", value_only=True)
    if ancestor_values and len(ancestor_values[0]) > 0:
        new_values = get_values(new_item, "planning", value_only=True)
        if not new_values or len(new_values[0]) < 1:
            return scope, False

    ancestor_values = get_values(item, "awards", value_only=True)
    if ancestor_values and len(ancestor_values) > 0:
        new_values = get_values(new_item, "awards", value_only=True)
        if not new_values or len(new_values) < len(ancestor_values):
            return scope, False

    ancestor_values = get_values(item, "contracts", value_only=True)
    if ancestor_values and len(ancestor_values) > 0:
        new_values = get_values(new_item, "contracts", value_only=True)
        if not new_values or len(new_values) < len(ancestor_values):
            return scope, False

    return scope, True
