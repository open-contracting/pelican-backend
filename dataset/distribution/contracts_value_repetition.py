
from dataset.distribution.value_repetition import \
    add_item as common_add_item, \
    get_result as common_get_result


def add_item(scope, item, item_id):
    return common_add_item(scope, item, item_id, 'contracts')


def get_result(scope):
    return common_get_result(scope)
