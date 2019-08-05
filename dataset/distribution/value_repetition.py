

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
examples_cap = 10


def add_item(scope, item, item_id, path):
    values = get_values(item, '{}.value'.format(path))
    if not values:
        return scope

    values = [v['value'] for v in values]

    # check whether amount and currency fields are set
    values = [
        v for v in values
        if (
            'amount' in v and 'currency' in v and
            v['amount'] and v['currency']
        )
    ]

    # intermediate computation
    for value in values:
        if not scope:
            scope = {}

        key = '{},{}'.format(value['amount'], value['currency'])
        if key not in scope:
            scope[key] = {
                'value.amount': value['amount'],
                'value.currency': value['currency'],
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

    if scope is not None:
        total_count = 0
        most_frequent = []

        # determine three most frequent value.amount and value.currency
        # combinations
        for key in scope:
            most_frequent.append(key)
            most_frequent.sort(key=lambda k: scope[k]['count'], reverse=True)
            most_frequent = most_frequent[:3]

            total_count += scope[key]['count']

        if total_count == 0:
            result['meta'] = {
                'reason': ('total count of distinct value.amount and '
                           'value.currency is zero')
            }
            return result

        most_frequent_count = sum([scope[k]['count'] for k in most_frequent])

        ratio = (most_frequent_count / total_count)
        passed = ratio < 0.1

        result['result'] = passed
        result['value'] = ratio
        result['meta'] = most_frequent

    return result


