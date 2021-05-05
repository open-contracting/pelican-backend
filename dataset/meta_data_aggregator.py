
import copy
from datetime import date

import psycopg2.extras
import requests
import simplejson as json
from dateutil.relativedelta import relativedelta

from contracting_process.field_level.definitions import coverage_checks, definitions
from settings.settings import get_param
from tools.currency_converter import convert
from tools.db import get_cursor
from tools.getter import get_values
from tools.helpers import parse_datetime

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
    rel_date = None
    if "date" in item:
        rel_datetime = parse_datetime(item['date'])
        rel_date = rel_datetime.date() if rel_datetime else None
    values = get_values(item, 'contracts.value', value_only=True)
    for value in values:
        # check whether relevant field are set
        if 'amount' not in value or 'currency' not in value or \
                value['amount'] is None or value['currency'] is None:
            continue

        amount_usd = convert(value['amount'], value['currency'], 'USD', rel_date)
        if amount_usd is None:
            continue

        amount_usd = int(amount_usd)

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


def get_result(scope):
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


EMPTY_KINGFISHER_META_DATA = {
    'kingfisher_metadata': {
        'collection_id': None,
        'processing_start': None,
        'processing_end': None
    },
    'collection_metadata': {
        'publisher': None,
        'url': None,
        'ocid_prefix': None,
        'data_license': None,
        'publication_policy': None,
        'extensions': [],
        'published_from': None,
        'published_to': None
    }
}
DATETIME_STR_FORMAT = '%Y-%m-%d %H.%M.%S'


def get_kingfisher_meta_data(collection_id):
    kf_connection = psycopg2.connect("host='{}' dbname='{}' user='{}' password='{}' port ='{}'".format(
        get_param("kf_extractor_host"),
        get_param("kf_extractor_db"),
        get_param("kf_extractor_user"),
        get_param("kf_extractor_password"),
        get_param("kf_extractor_port")))

    kf_cursor = kf_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    meta_data = copy.deepcopy(EMPTY_KINGFISHER_META_DATA)

    #######################
    # kingfisher metadata #
    #######################
    meta_data['kingfisher_metadata'] = {}
    kf_cursor.execute(
        """
        SELECT c.id, c.store_start_at, a.store_end_at
        FROM collection AS a
        INNER JOIN collection AS b ON a.transform_from_collection_id = b.id
        INNER JOIN collection AS c ON b.transform_from_collection_id = c.id
        AND a.id = %s
        LIMIT 1;
        """, (collection_id,)
    )
    result = kf_cursor.fetchone()

    if result is None:
        return meta_data

    meta_data['kingfisher_metadata']['collection_id'] = collection_id
    if result[1]:
        meta_data['kingfisher_metadata']['processing_start'] = result[1].strftime(DATETIME_STR_FORMAT)
    if result[2]:
        meta_data['kingfisher_metadata']['processing_end'] = result[2].strftime(DATETIME_STR_FORMAT)

    ##########################################
    # retrieving additional database entries #
    ##########################################
    proprietary_id = result[0]
    with_collection = None
    package_data = None

    # with collection
    kf_cursor.execute(
        """
        SELECT *
        FROM release
        WHERE collection_id = %s
        LIMIT 1;
        """, (proprietary_id,)
    )
    result = kf_cursor.fetchone()
    if result is None:
        kf_cursor.execute(
            """
            SELECT *
            FROM record
            WHERE collection_id = %s
            LIMIT 1;
            """, (proprietary_id,)
        )
        result = kf_cursor.fetchone()

    if result is None:
        return meta_data

    with_collection = result

    # package data
    kf_cursor.execute(
        """
        SELECT *
        FROM package_data
        WHERE id = %s
        LIMIT 1;
        """, (with_collection['package_data_id'],)
    )
    package_data = kf_cursor.fetchone()
    package_data = package_data if package_data else {}

    #######################
    # collection metadata #
    #######################

    # publisher
    values = get_values(package_data, 'data.publisher.name', value_only=True)
    if values:
        meta_data['collection_metadata']['publisher'] = values[0]

    # url
    meta_data['collection_metadata']['url'] = 'The URL where the data can be downloaded isn\'t presently available.'

    # ocid prefix
    values = get_values(with_collection, 'ocid', value_only=True)
    if values and type(values[0]) == str:
        meta_data['collection_metadata']['ocid_prefix'] = values[0][:11]

    # data license
    values = get_values(package_data, 'data.license', value_only=True)
    if values:
        meta_data['collection_metadata']['data_license'] = values[0]

    # publication policy
    values = get_values(package_data, 'data.publicationPolicy', value_only=True)
    if values:
        meta_data['collection_metadata']['publication_policy'] = values[0]

    # extensions
    repository_urls = get_values(package_data, 'data.extensions', value_only=True)
    for repository_url in repository_urls:
        try:
            request = requests.get(repository_url, timeout=30)
            if request.status_code != 200:
                continue

            extension = request.json()
            extension['repositoryUrl'] = repository_url
            meta_data['collection_metadata']['extensions'].append(extension)

        except:
            pass

    # published from, published to
    kf_cursor.execute(
        """
        SELECT MIN(data.data->>'date'), MAX(data.data->>'date')
        FROM compiled_release
        JOIN data
        ON compiled_release.data_id = data.id
        WHERE compiled_release.collection_id = %s AND
            data.data ? 'date' AND
            data.data->>'date' is not null AND
            data.data->>'date' <> ''
        LIMIT 1;
        """, (collection_id,)
    )
    result = kf_cursor.fetchone()
    meta_data['collection_metadata']['published_from'] = \
        parse_datetime(result[0]).strftime(DATETIME_STR_FORMAT) if (result is not None and result[0] is not None) else None
    meta_data['collection_metadata']['published_to'] = \
        parse_datetime(result[1]).strftime(DATETIME_STR_FORMAT) if (result is not None and result[1] is not None) else None

    return meta_data


EMPTY_DQT_META_DATA = {
    'data_quality_tool_metadata': {
        'processing_start': None,
        'processing_end': None
    }
}


def get_dqt_meta_data(dataset_id):
    cursor = get_cursor()

    meta_data = copy.deepcopy(EMPTY_DQT_META_DATA)

    cursor.execute(
        """
        SELECT created, now()
        FROM dataset
        WHERE id = %s;
        """, (dataset_id,)
    )

    row = cursor.fetchone()
    meta_data['data_quality_tool_metadata']['processing_start'] = row[0].strftime(DATETIME_STR_FORMAT)
    meta_data['data_quality_tool_metadata']['processing_end'] = row[1].strftime(DATETIME_STR_FORMAT)

    return meta_data


def update_meta_data(meta_data, dataset_id):
    cursor = get_cursor()
    cursor.execute(
        """
        UPDATE dataset
        SET meta = meta || %s, modified = now()
        WHERE id = %s;
        """, (json.dumps(meta_data), dataset_id)
    )
