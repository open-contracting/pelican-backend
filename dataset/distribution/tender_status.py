
import random

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
samples_num = 20
possible_status = [
    'planning', 'planned', 'active', 'cancelled', 'unsuccessufl', 'complete', 'withdrawn'
]


def add_item(scope, item, item_id):
    if not scope:
        scope = {
            status: {'count': 0, 'examples_id': []}
            for status in possible_status
        }

    values = get_values(item, 'tender.status')
    values = [
        v['value'] for v in values
        if v['value'] in possible_status
    ]

    if not values:
        return scope

    status = values[0]

    # reservoir sampling
    if scope[status]['count'] < samples_num:
        scope[status]['examples_id'].append(item_id)
    else:
        r = random.randint(0, scope[status]['count'])
        if r < samples_num:
            scope[status]['examples_id'][r] = item_id

    scope[status]['count'] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if not scope:
        result['meta'] = {
            'reason': 'no data items were processed'
        }

        return result

    total_valid_status = sum([scope[status]['count'] for status in scope])
    if total_valid_status == 0:
        result['meta'] = {
            'reason': 'there is not a single tender with valid status'
        }

        return result

    ratio = (scope['active']['count'] + scope['complete']['count']) / total_valid_status
    passed = 0.01 <= ratio <= 0.99

    for _, value in scope.items():
        value['share'] = value['count'] / total_valid_status
        value.pop('count', None)

    result['result'] = passed
    result['value'] = 100 if passed else 0
    result['meta'] = {
        'status': scope
    }

    return result