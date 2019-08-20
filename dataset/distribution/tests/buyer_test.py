

from dataset.distribution import buyer


def test_undefined():
    scope = {}
    result = buyer.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'no data items were processed'
    }

    scope = {}
    scope = buyer.add_item(scope, {'ocid': '0'}, 0)
    result = buyer.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there are not enough resources with check-specific properties'
    }

items_test_undefined_multiple1 = [
    {
        'ocid': '0',
    },
    {
        'ocid': '1',
        'buyer': {

        }
    },
    {
        'ocid': '2',
        'buyer': {
            'identifier': {

            }
        }
    },
    {
        'ocid': '3',
        'buyer': {
            'identifier': {
                'scheme': None,
                'id': None
            }
        }
    },
    {
        'ocid': '4',
        'buyer': {
            'identifier': {
                'scheme': 'ICO',
                'id': None
            }
        }
    },
    {
        'ocid': '5',
        'buyer': {
            'identifier': {
                'scheme': None,
                'id': '5'
            }
        }
    }
]

items_test_undefined_multiple2 = [
    {
        'ocid': '0',
        'buyer': {
            'identifier': {
                'scheme': 'ICO',
                'id': '0'
            }
        }
    }
    for _ in range(buyer.min_resources_num - 1)
]


def test_undefined_multiple():
    scope = {}

    id = 0
    for item in items_test_undefined_multiple1:
        scope = buyer.add_item(scope, item, id)
        id += 1

    result = buyer.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there are not enough resources with check-specific properties'
    }

    scope = {}

    id = 0
    for item in items_test_undefined_multiple2:
        scope = buyer.add_item(scope, item, id)
        id += 1

    result = buyer.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there are not enough resources with check-specific properties'
    }

items_test_failed1 = [
    {
        'ocid': num,
        'buyer': {
            'identifier': {
                'scheme': 'ICO',
                'id': 0
            }
        }
    }
    for num in range(buyer.min_resources_num)
]

items_test_failed2 = [
    {
        'ocid': '0',
        'buyer': {
            'identifier': {
                'scheme': 'ICO',
                'id': num
            }
        }
    }
    for num in range(buyer.min_resources_num)
]


def test_failed():
    scope = {}

    id = 0
    for item in items_test_failed1:
        scope = buyer.add_item(scope, item, id)
        id += 1

    result = buyer.get_result(scope)
    assert result['result'] is False
    assert result['value'] == 0
    assert result['meta']['total_ocid_count'] == buyer.min_resources_num
    assert result['meta']['counts']['100+'] == {
        'buyer_count': 1,
        'ocid_count': 1000
    }
    assert len(result['meta']['examples']['single_ocid_examples_id']) == 0
    assert len(result['meta']['examples']['max_ocid_examples_id']) == buyer.examples_id_cap

    scope = {}

    id = 0
    for item in items_test_failed2:
        scope = buyer.add_item(scope, item, id)
        id += 1

    result = buyer.get_result(scope)
    assert result['result'] is False
    assert result['value'] == 0
    assert result['meta']['total_ocid_count'] == 1
    assert result['meta']['counts']['1'] == {
        'buyer_count': 1000,
        'ocid_count': 1
    }
    assert len(result['meta']['examples']['single_ocid_examples_id']) == buyer.examples_id_cap
    assert len(result['meta']['examples']['max_ocid_examples_id']) == 1

items_test_passed_multiple = []
items_test_passed_multiple.extend(
    [
        {
            'ocid': '0',
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': num
                }
            }
        }
        for num in range(200)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': str(num2),
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': num1
                }
            }
        }
        for num1 in range(200, 400) for num2 in range(10, 20)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': str(num2),
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': num1
                }
            }
        }
        for num1 in range(400, 600) for num2 in range(20, 50)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': str(num2),
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': num1
                }
            }
        }
        for num1 in range(600, 800) for num2 in range(50, 110)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': str(num2),
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': num1
                }
            }
        }
        for num1 in range(800, 1000) for num2 in range(110, 211)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': str(num),
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': 1000
                }
            }
        }
        for num in range(211, 313)
    ]
)


# working when min_resources_num is set to 1000
def test_passed_multiple():
    scope = {}

    id = 0
    for item in items_test_passed_multiple:
        scope = buyer.add_item(scope, item, id)
        id += 1

    result = buyer.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert result['meta']['total_ocid_count'] == 313 - 9
    assert result['meta']['counts'] == {
        '1': {'ocid_count': 1, 'buyer_count': 200},
        '2_20': {'ocid_count': 10, 'buyer_count': 200},
        '21_50': {'ocid_count': 30, 'buyer_count': 200},
        '51_100': {'ocid_count': 60, 'buyer_count': 200},
        '100+': {'ocid_count': 313 - 110, 'buyer_count': 201}
    }
    assert result['meta']['shares'] == {
        '1': {
            'ocid_share': 1 / result['meta']['total_ocid_count'],
            'buyer_share': 200 / result['meta']['total_buyer_count']
        },
        '2_20': {
            'ocid_share': 10 / result['meta']['total_ocid_count'],
            'buyer_share': 200 / result['meta']['total_buyer_count']
        },
        '21_50': {
            'ocid_share': 30 / result['meta']['total_ocid_count'],
            'buyer_share': 200 / result['meta']['total_buyer_count']
        },
        '51_100': {
            'ocid_share': 60 / result['meta']['total_ocid_count'],
            'buyer_share': 200 / result['meta']['total_buyer_count']
        },
        '100+': {
            'ocid_share': (313 - 110) / result['meta']['total_ocid_count'],
            'buyer_share': 201 / result['meta']['total_buyer_count']
        }
    }
    assert len(result['meta']['examples']['single_ocid_examples_id']) == buyer.examples_id_cap
    assert len(result['meta']['examples']['max_ocid_examples_id']) == buyer.examples_id_cap
    assert sum([value['ocid_count'] for value in result['meta']['counts'].values()]) == \
        result['meta']['total_ocid_count']
    assert sum([value['buyer_count'] for value in result['meta']['counts'].values()]) == \
        result['meta']['total_buyer_count']
