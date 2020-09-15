
import random

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 2.0
examples_cap = 100


def add_item(scope, item, item_id):
    if not scope:
        scope = {
            'original_ocid': dict(),
            'related_processes': dict(),
            'meta': {
                'total_processed': 0,
                'total_passed': 0,
                'total_failed': 0,
                'passed_examples': [],
                'failed_examples': []
            }
        }

    ocid = item['ocid']

    if ocid:
        if ocid in scope['original_ocid']:
            scope['original_ocid'][ocid]['found'] = True
            for key in scope['original_ocid'][ocid]['pending_related_processes']:
                scope = pick_examples(scope, key, True)
                del scope['related_processes'][key]

            scope['original_ocid'][ocid]['pending_related_processes'].clear()
        else:
            scope['original_ocid'][ocid] = {
                'pending_related_processes': [],
                'found': True
            }

    related_processes = []
    related_processes.extend(get_values(item, 'relatedProcesses'))
    related_processes.extend(get_values(item, 'contracts.relatedProcesses'))

    for related_process in related_processes:
        # checking if all required fields are set
        if 'scheme' not in related_process['value'] or related_process['value']['scheme'] != 'ocid':
            continue

        if 'identifier' not in related_process['value'] or related_process['value']['identifier'] is None:
            continue

        key = (ocid, related_process['value']['identifier'])
        scope['related_processes'][key] = {
            'item_id': item_id,
            'ocid': ocid,
            'related_ocid': related_process['value']['identifier'],
            'related_path': related_process['path']
        }

        if related_process['value']['identifier'] in scope['original_ocid']:
            if scope['original_ocid'][related_process['value']['identifier']]['found']:
                scope = pick_examples(scope, key, True)
                del scope['related_processes'][key]
            else:
                scope['original_ocid'][related_process['value']['identifier']]['pending_related_processes'].append(key)

        else:
            scope['original_ocid'][related_process['value']['identifier']] = {
                'pending_related_processes': [key],
                'found': False
            }

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    for key in scope['related_processes']:
        scope = pick_examples(scope, key, False)

    if scope['meta']['total_processed'] == 0:
        result['meta'] = {
            'reason': 'there are no pairs of related processes with check-specific properties'
        }
    else:
        result['result'] = scope['meta']['total_passed'] == scope['meta']['total_processed']
        result['value'] = 100 * (scope['meta']['total_passed'] / scope['meta']['total_processed'])
        result['meta'] = scope['meta']

    return result


def pick_examples(scope, related_process_key, result):
    example = {
        'item_id': scope['related_processes'][related_process_key]['item_id'],
        'ocid': scope['related_processes'][related_process_key]['ocid'],
        'related_process': scope['related_processes'][related_process_key],
        'result': result
    }

    if result:
        if scope['meta']['total_passed'] < examples_cap:
            scope['meta']['passed_examples'].append(example)
        else:
            r = random.randint(0, scope['meta']['total_passed'])
            if r < examples_cap:
                scope['meta']['passed_examples'][r] = example

        scope['meta']['total_passed'] += 1
    else:
        if scope['meta']['total_failed'] < examples_cap:
            scope['meta']['failed_examples'].append(example)
        else:
            r = random.randint(0, scope['meta']['total_failed'])
            if r < examples_cap:
                scope['meta']['failed_examples'][r] = example

        scope['meta']['total_failed'] += 1

    scope['meta']['total_processed'] += 1

    return scope
