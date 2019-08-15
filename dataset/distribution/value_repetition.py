
import functools

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
examples_cap = 10


class ModuleType:
    def __init__(self, path):
        self.add_item = functools.partial(add_item, path=path)
        self.get_result = get_result


def add_item(scope, item, item_id, path):
    if scope is None:
        scope = {}

    values = get_values(item, '{}.value'.format(path))
    if not values:
        return scope

    values = [v['value'] for v in values]

    # check whether amount and currency fields are set
    values = [
        v for v in values
        if (
            'amount' in v and 'currency' in v and
            v['amount'] is not None and v['currency'] is not None
        )
    ]

    # intermediate computation
    for value in values:
        key = '{},{}'.format(value['amount'], value['currency'])
        if key not in scope:
            scope[key] = {
                'value': value,
                'count': 1,
                'examples_id': [item_id]
            }
        else:
            scope[key]['count'] += 1
            if item_id not in scope[key]['examples_id'] and \
                    len(scope[key]['examples_id']) < examples_cap:
                scope[key]['examples_id'].append(item_id)

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if scope:
        total_count = 0
        most_frequent = []

        # determine three most frequent value.amount and value.currency combinations
        for key in scope:
            most_frequent.append(key)
            most_frequent.sort(key=lambda k: scope[k]['count'], reverse=True)
            most_frequent = most_frequent[:3]

            total_count += scope[key]['count']

        most_frequent_count = sum([scope[k]['count'] for k in most_frequent])

        ratio = (most_frequent_count / total_count)
        passed = ratio < 0.1

        for key in most_frequent:
            scope[key]['share'] = scope[key]['count'] / total_count

        result['result'] = passed
        result['value'] = ratio
        result['meta'] = {
            'most_frequent': [
                scope[key] for key in most_frequent
            ],
            'total_processed': total_count
        }
    else:
        result['meta'] = {'reason': 'there are is no suitable data item for this check'}

    return result
