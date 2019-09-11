

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
    for num in range(int(0.6 * buyer.min_resources_num))
]
items_test_failed2.extend(
    [
        {
            'ocid': '0',
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': -1
                }
            }
        }
        for _ in range(int(0.4 * buyer.min_resources_num))
    ]
)


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
    assert result['meta']['counts']['1'] == buyer.min_resources_num
    assert len(result['meta']['examples']) == buyer.examples_cap

    scope = {}

    id = 0
    for item in items_test_failed2:
        scope = buyer.add_item(scope, item, id)
        id += 1

    result = buyer.get_result(scope)
    assert result['result'] is False
    assert result['value'] == 0
    assert result['meta']['total_ocid_count'] == buyer.min_resources_num
    assert result['meta']['counts']['1'] == 0.6 * buyer.min_resources_num
    assert result['meta']['counts']['100+'] == 0.4 * buyer.min_resources_num
    assert len(result['meta']['examples']) == buyer.examples_cap

items_test_passed_multiple = []
items_test_passed_multiple.extend(
    [
        {
            'ocid': '0',
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': id
                }
            }
        }
        for id in range(100)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': '0',
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': id
                }
            }
        }
        for _ in range(1, 3) for id in range(100, 200)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': '0',
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': id
                }
            }
        }
        for _ in range(3, 24) for id in range(200, 300)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': '0',
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': id
                }
            }
        }
        for _ in range(24, 75) for id in range(300, 400)
    ]
)
items_test_passed_multiple.extend(
    [
        {
            'ocid': '0',
            'buyer': {
                'identifier': {
                    'scheme': 'ICO',
                    'id': id
                }
            }
        }
        for _ in range(75, 176) for id in range(400, 500)
    ]
)


def test_passed_multiple():
    scope = {}

    id = 0
    for item in items_test_passed_multiple:
        scope = buyer.add_item(scope, item, id)
        id += 1

    result = buyer.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert result['meta']['total_ocid_count'] == 100 * 176
    assert result['meta']['counts']['1'] == 100 * 1
    assert result['meta']['counts']['2_20'] == 100 * 2
    assert result['meta']['counts']['21_50'] == 100 * 21
    assert result['meta']['counts']['51_100'] == 100 * 51
    assert result['meta']['counts']['100+'] == 100 * 101
    assert len(result['meta']['examples']) == buyer.examples_cap
