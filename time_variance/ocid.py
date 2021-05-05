
from tools.checks import get_empty_result_time_variance
from tools.getter import get_values

version = 1.0


def filter(scope, item, item_id, new_item, new_item_id):
    # entry filtering - check makes sense for all the items
    if item:
        return True

    return False


def evaluate(scope, item, item_id, new_item, new_item_id):
    if item and new_item:
        return scope, True

    return scope, False
