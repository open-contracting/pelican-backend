import operator

from dataset.distribution.common import add_item as common_add_item
from dataset.distribution.common import get_result as common_get_result
from tools.checks import get_empty_result_dataset
from tools.getter import get_values
from tools.helpers import parse_date

version = 1.0


def add_item(scope, item, item_id):
    return common_add_item(scope, item, item_id, "tender.value")


def get_result(scope):
    return common_get_result(scope)
