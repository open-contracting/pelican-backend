
import random

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
min_resources_num = 1000
examples_id_cap = 20


def add_item(scope, item, item_id):
    # scope initialization
    if not scope:
        scope = {
            'buyers': {},
            'ocid_set': set(),
            'resources_num': 0
        }

    # filtering values containing required fields
    values = get_values(item, 'buyer.identifier')
    buyers = [
        v['value'] for v in values
        if (
            'scheme' in v['value'] and 'id' in v['value'] and
            v['value']['scheme'] is not None and v['value']['id'] is not None
        )
    ]

    ocid = get_values(item, 'ocid')[0]['value']
    scope['ocid_set'].add(ocid)
    for buyer in buyers:
        scope['resources_num'] += 1
        key = (buyer['scheme'], buyer['id'])

        if key not in scope['buyers']:
            scope['buyers'][key] = {
                'scheme': buyer['scheme'],
                'id': buyer['id'],
                'ocid_set': set(),
                'examples_id': []
            }

        scope['buyers'][key]['ocid_set'].add(ocid)
        scope['buyers'][key]['examples_id'].append(item_id)

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if scope:
        if scope['resources_num'] < min_resources_num:
            result['meta'] = {
                'reason': 'there are not enough resources with check-specific properties'
            }
            return result

        # initializing histogram
        ocid_histogram = {
            '1': {'buyers': [], 'ocid_set': set()},
            '2-20': {'buyers': [], 'ocid_set': set()},
            '21-50': {'buyers': [], 'ocid_set': set()},
            '51-100': {'buyers': [], 'ocid_set': set()},
            '100+': {'buyers': [], 'ocid_set': set()}
        }

        # filling in the histogram
        max_buyer = {'buyer': None, 'ocid_count': -1}
        for buyer, value in scope['buyers'].items():
            ocid_count = len(value['ocid_set'])
            if ocid_count == 1:
                ocid_histogram['1']['buyers'].append(buyer)
                ocid_histogram['1']['ocid_set'].update(value['ocid_set'])
            elif 2 <= ocid_count <= 20:
                ocid_histogram['2-20']['buyers'].append(buyer)
                ocid_histogram['2-20']['ocid_set'].update(value['ocid_set'])
            elif 21 <= ocid_count <= 50:
                ocid_histogram['21-50']['buyers'].append(buyer)
                ocid_histogram['21-50']['ocid_set'].update(value['ocid_set'])
            elif 51 <= ocid_count <= 100:
                ocid_histogram['51-100']['buyers'].append(buyer)
                ocid_histogram['51-100']['ocid_set'].update(value['ocid_set'])
            else:
                ocid_histogram['100+']['buyers'].append(buyer)
                ocid_histogram['100+']['ocid_set'].update(value['ocid_set'])

            if ocid_count > max_buyer['ocid_count']:
                max_buyer['buyer'] = buyer
                max_buyer['ocid_count'] = ocid_count

        for value in ocid_histogram.values():
            value['ocid_count'] = len(value['ocid_set'])
            value['buyer_count'] = len(value['buyers'])

            value.pop('ocid_set', None)

        # checking whether the check passed or not
        total_ocid_count = len(scope['ocid_set'])
        max_ocid_count = max_buyer['ocid_count']
        single_ocid_count = ocid_histogram['1']['ocid_count']
        passed = (
            max_ocid_count > 0.01 * total_ocid_count and
            max_ocid_count < 0.5 * total_ocid_count and
            single_ocid_count < 0.5 * total_ocid_count
        )

        # sampling item_ids from buyers appearing in items with one distinct ocid
        single_ocid_examples_id = [
            random.choice(scope['buyers'][buyer]['examples_id'])
            for buyer in random.sample(
                ocid_histogram['1']['buyers'],
                k=examples_id_cap
                if examples_id_cap < len(ocid_histogram['1']['buyers'])
                else len(ocid_histogram['1']['buyers'])
            )
        ]

        # sampling item_ids from buyer that appeard in items with the most distinct ocids
        max_ocid_examples_id = random.sample(
            scope['buyers'][max_buyer['buyer']]['examples_id'],
            k=examples_id_cap
            if examples_id_cap < len(scope['buyers'][max_buyer['buyer']]['examples_id'])
            else len(scope['buyers'][max_buyer['buyer']]['examples_id'])
        )

        for value in ocid_histogram.values():
            value.pop('buyers', None)

        result['result'] = passed
        result['value'] = None
        result['meta'] = {
            'total_ocid_count': total_ocid_count,
            'ocid_histogram': ocid_histogram,
            'single_ocid_examples_id': single_ocid_examples_id,
            'max_ocid_examples_id': max_ocid_examples_id
        }
    else:
        result['meta'] = {
            'reason': 'no data items were processed'
        }

    return result
