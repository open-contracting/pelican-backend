
import random
from collections import defaultdict

from tools.checks import get_empty_result_dataset
from tools.getter import get_values


def add_item(scope, item, item_id):
    if not scope:
        scope = {'tender_id_mapping': defaultdict(list)}

    ocid = item['ocid']
    values = get_values(item, 'tender.id', value_only=True)
    if not values:
        return scope

    tender_id = str(values[0])
    scope['tender_id_mapping'][tender_id].append(ocid)

    return scope


def get_result(scope):
    result = get_empty_result_dataset()

    if not scope or not scope['tender_id_mapping']:
        result['meta'] = {'reason': 'there are no tenders with check-specific properties'}
        return result

    result['meta'] = {'failed_examples': []}
    relevant_releases_count = sum(len(v) for v in scope['tender_id_mapping'].values())
    passed_releases_count = sum(len(v) for v in scope['tender_id_mapping'].values() if len(v) == 1)
    if relevant_releases_count == passed_releases_count:
        result['result'] = True
        result['value'] = 100 * passed_releases_count / relevant_releases_count
    else:
        result['result'] = False
        result['value'] = 100 * passed_releases_count / relevant_releases_count
        result['meta']['failed_examples'] = [
            {
                'tender_id': tender_id,
                'ocids': random.sample(ocids, min(100, len(ocids)))
            }
            for tender_id, ocids in scope['tender_id_mapping'].items()
            if len(ocids) > 1
        ]

    return result
