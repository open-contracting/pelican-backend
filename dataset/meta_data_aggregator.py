
import copy
from datetime import date
from dateutil.relativedelta import relativedelta

from tools.helpers import parse_datetime
from tools.getter import get_values
from tools.currency_converter import convert

EMPTY_SCOPE = {
    'compiled_releases': {
        'total_unique_ocids': None,
        '_ocid_set': set()
    },
    'tender_lifecycle': {
        'planning': 0,
        'tender': 0,
        'award': 0,
        'contract': 0,
        'implementation': 0
    },
    'prices': {
        'total_volume_positive': 0,
        'contracts_positive': 0,
        'total_volume_negative': 0,
        'contracts_negative': 0,
        'price_category_positive': {
            '0_10000': {
                'contracts': 0,
                'volume': 0,
                'share': None
            },
            '10001_100000': {
                'contracts': 0,
                'volume': 0,
                'share': None
            },
            '100001_1000000': {
                'contracts': 0,
                'volume': 0,
                'share': None
            },
            '1000001+': {
                'contracts': 0,
                'volume': 0,
                'share': None
            }
        }
    },
    '_period_dict': dict(),
    'period': None
}
DATE_STR_FORMAT = '%b-%-y'


def add_item(scope, item, item_id):
    if not scope:
        scope = copy.deepcopy(EMPTY_SCOPE)

    # compiled releases
    scope['compiled_releases']['_ocid_set'].add(item['ocid'])

    # tender lifecycle
    scope['tender_lifecycle']['planning'] += len(get_values(item, 'planning'))
    scope['tender_lifecycle']['tender'] += len(get_values(item, 'tender'))
    scope['tender_lifecycle']['award'] += len(get_values(item, 'awards'))
    scope['tender_lifecycle']['contract'] += len(get_values(item, 'contracts'))
    scope['tender_lifecycle']['implementation'] += len(get_values(item, 'contracts.implementation'))

    # prices
    rel_datetime = parse_datetime(item['date']) 
    rel_date = rel_datetime.date() if rel_datetime else None
    values = get_values(item, 'contracts.value', value_only=True)
    for value in values:
        # check whether relevant field are set
        if 'amount' not in value or 'currency' not in value or \
                value['amount'] is None or value['currency'] is None:
            continue

        amount_usd = int(convert(value['amount'], value['currency'], 'USD', rel_date))
        if amount_usd is None:
            continue

        if amount_usd >= 0:
            scope['prices']['total_volume_positive'] += amount_usd
            scope['prices']['contracts_positive'] += 1

            if 0 <= amount_usd <= 10000:
                scope['prices']['price_category_positive']['0_10000']['volume'] += amount_usd
                scope['prices']['price_category_positive']['0_10000']['contracts'] += 1
            elif 10001 <= amount_usd <= 100000:
                scope['prices']['price_category_positive']['10001_100000']['volume'] += amount_usd
                scope['prices']['price_category_positive']['10001_100000']['contracts'] += 1
            elif 100001 <= amount_usd <= 1000000:
                scope['prices']['price_category_positive']['100001_1000000']['volume'] += amount_usd
                scope['prices']['price_category_positive']['100001_1000000']['contracts'] += 1
            else:
                scope['prices']['price_category_positive']['1000001+']['volume'] += amount_usd
                scope['prices']['price_category_positive']['1000001+']['contracts'] += 1
        else:
            scope['prices']['total_volume_negative'] += amount_usd
            scope['prices']['contracts_negative'] += 1

    # period
    if rel_date:
        period = rel_date.replace(day=1)
        if period not in scope['_period_dict']:
            scope['_period_dict'][period] = 1
        else:
            scope['_period_dict'][period] += 1

    return scope


def get_meta_data(scope):
    # compiled releases
    scope['compiled_releases']['total_unique_ocids'] = len(scope['compiled_releases']['_ocid_set'])
    del scope['compiled_releases']['_ocid_set']

    # prices
    for key in scope['prices']['price_category_positive']:
        if scope['prices']['total_volume_positive'] == 0:
            scope['prices']['price_category_positive'][key]['share'] = 0
        else:
            scope['prices']['price_category_positive'][key]['share'] = \
                scope['prices']['price_category_positive'][key]['volume'] / scope['prices']['total_volume_positive']

    # period
    min_date = min(scope['_period_dict'])
    max_date = max(scope['_period_dict'])

    scope['period'] = []
    current_date = min_date
    while current_date <= max_date:
        if current_date in scope['_period_dict']:
            scope['period'].append(
                {
                    'date_str': current_date.strftime(DATE_STR_FORMAT),
                    'count': scope['_period_dict'][current_date]
                }
            )
        else:
            scope['period'].append(
                {
                    'date_str': current_date.strftime(DATE_STR_FORMAT),
                    'count': 0
                }
            )

        current_date += relativedelta(months=+1)

    del scope['_period_dict']

    return scope
