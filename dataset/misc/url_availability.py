import random
import requests

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
samples_num = 100

paths = [
    'planning.documents.url',
    'tender.documents.url',
    'awards.documents.url',
    'contracts.documents.url'
]


def add_item(scope, item, item_id):
    values = []
    for path in paths:
        pos_values = get_values(item, path)
        if not pos_values:
            continue

        for value in pos_values:
            value['item_id'] = item_id
            if value['value'] is not None:
                values.append(value)

    # reservoir sampling
    for value in values:
        if scope['index'] < samples_num:
            scope['samples'].append(value)
        else:
            r = random.randint(0, scope['index'])
            if r < samples_num:
                scope['samples'][r] = value

        scope['index'] += 1

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if scope is None:
        result['meta'] = {'reason': 'missing scope'}
        return result

    # not enough urls
    if len(scope['samples']) < samples_num:
        result['meta'] = {
            'reason': 'there is less than {} URLs in the dataset'
            .format(samples_num)
        }
        return result

    # checking url status
    ok_status_num = 0
    for sample in scope['samples']:
        try:
            request = requests.get(sample['value'], timeout=30, stream=True)
            if 200 <= request.status_code < 400:
                sample['status'] = 'OK'
                ok_status_num += 1
            else:
                sample['status'] = 'ERROR'
        except:
            sample['status'] = 'ERROR'

    result['result'] = ok_status_num == samples_num
    result['value'] = 100 * (ok_status_num / samples_num)
    result['meta'] = {'samples': scope['samples']}

    return result
