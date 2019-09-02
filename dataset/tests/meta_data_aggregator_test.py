
from dataset.meta_data_aggregator import add_item, get_result
from tools.bootstrap import bootstrap

bootstrap('test', 'meta_data_aggregator_test')


items_test_compiled_releases = [
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00'
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00'
    },
    {
        'ocid': '1',
        'date': '2019-01-10T22:00:00+01:00'
    }
]


def test_compiled_releases():
    scope = {}
    for id in range(len(items_test_compiled_releases)):
        scope = add_item(scope, items_test_compiled_releases[id], id)
    result = get_result(scope)

    assert result['compiled_releases']['total_unique_ocids'] == 2
    assert sum(
        [value for value in result['tender_lifecycle'].values()]
    ) == 0
    assert result['period'] == [{'date_str': 'Jan-19', 'count': 3}]

items_test_tender_lifecycle = [
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'tender': {}
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'tender': {},
        'planning': {}
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'contracts': [{}, {}, {}]
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'awards': [{}, {}, {}]
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'contracts': [
            {
                'implementation': {}
            }
        ]
    }
]


def test_tender_lifecycle():
    scope = {}
    for id in range(len(items_test_tender_lifecycle)):
        scope = add_item(scope, items_test_tender_lifecycle[id], id)
    result = get_result(scope)

    assert result['compiled_releases']['total_unique_ocids'] == 1
    assert result['tender_lifecycle'] == {
        'planning': 1,
        'tender': 2,
        'award': 3,
        'contract': 4,
        'implementation': 1
    }
    assert result['period'] == [{'date_str': 'Jan-19', 'count': 5}]

items_test_prices = [
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'contracts': [
            {
                'value': {'amount': 2000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 2000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 2000, 'currency': 'USD'}
            }
        ]
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'contracts': [
            {
                'value': {'amount': 20000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 20000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 20000, 'currency': 'USD'}
            }
        ]
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'contracts': [
            {
                'value': {'amount': 200000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 200000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 200000, 'currency': 'USD'}
            }
        ]
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'contracts': [
            {
                'value': {'amount': 2000000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 2000000, 'currency': 'USD'}
            },
            {
                'value': {'amount': 2000000, 'currency': 'USD'}
            }
        ]
    },
    {
        'ocid': '0',
        'date': '2019-01-10T22:00:00+01:00',
        'contracts': [
            {
                'value': {'amount': -1, 'currency': 'USD'}
            },
            {
                'value': {'amount': -1, 'currency': 'USD'}
            },
            {
                'value': {'amount': -1, 'currency': 'USD'}
            }
        ]
    }
]


def test_prices():
    scope = {}
    for id in range(len(items_test_prices)):
        scope = add_item(scope, items_test_prices[id], id)
    result = get_result(scope)

    assert result['compiled_releases']['total_unique_ocids'] == 1
    assert result['tender_lifecycle'] == {
        'planning': 0,
        'tender': 0,
        'award': 0,
        'contract': 15,
        'implementation': 0
    }
    total_volume_positive = 3 * (2000 + 20000 + 200000 + 2000000)
    assert result['prices'] == {
        'total_volume_positive': total_volume_positive,
        'contracts_positive': 12,
        'total_volume_negative': -3,
        'contracts_negative': 3,
        'price_category_positive': {
            '0_10000': {
                'contracts': 3,
                'volume': 3 * 2000,
                'share': 3 * 2000 / total_volume_positive
            },
            '10001_100000': {
                'contracts': 3,
                'volume': 3 * 20000,
                'share': 3 * 20000 / total_volume_positive
            },
            '100001_1000000': {
                'contracts': 3,
                'volume': 3 * 200000,
                'share': 3 * 200000 / total_volume_positive
            },
            '1000001+': {
                'contracts': 3,
                'volume': 3 * 2000000,
                'share': 3 * 2000000 / total_volume_positive
            }
        }
    }
    assert result['period'] == [{'date_str': 'Jan-19', 'count': 5}]

items_test_period = [
    {
        'ocid': '0',
        'date': '2018-12-01T22:00:00+01:00',
    },
    {
        'ocid': '0',
        'date': '2019-01-01T22:00:00+01:00',
    },
    {
        'ocid': '0',
        'date': '2019-01-05T22:00:00+01:00',
    },
    {
        'ocid': '0',
        'date': '2019-03-25T22:00:00+01:00',
    }
]


def test_prices():
    scope = {}
    for id in range(len(items_test_period)):
        scope = add_item(scope, items_test_period[id], id)
    result = get_result(scope)

    assert result['compiled_releases']['total_unique_ocids'] == 1
    assert sum(
        [value for value in result['tender_lifecycle'].values()]
    ) == 0
    assert result['period'] == [
        {'date_str': 'Dec-18', 'count': 1},
        {'date_str': 'Jan-19', 'count': 2},
        {'date_str': 'Feb-19', 'count': 0},
        {'date_str': 'Mar-19', 'count': 1}
    ]
