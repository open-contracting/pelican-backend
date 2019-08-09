
import functools

from contracting_process.resource_level.consistent import roles
calculate = functools.partial(
    roles.calculate_path_role,
    path='contracts.implementation.transactions.payee',
    role='payee'
)

item_test_undefined1 = {
    'parties': [
        {
            'id': '0'
        }
    ]
}

item_test_undefined2 = {
    'parties': [
        {
            'id': '0'
        }
    ],
    'contracts': [
        {
            'implementation': {
                'transactions': [
                    {
                        'payee': {
                            
                        }
                    }
                ]
            }
        }
    ]
}

item_test_undefined3 = {
    'parties': [
        {
            'id': '0'
        },
        {
            'id': '0'
        }
    ],
    'contracts': [
        {
            'implementation': {
                'transactions': [
                    {
                        'payee': {
                           'id': '0'
                        }
                    }
                ]
            }
        }
    ]
}


def test_undefined():
    result = calculate({})
    assert result['result'] is None
    assert result['value'] is None
    assert result['application_count'] is None
    assert result['pass_count'] is None
    assert result['meta'] == {
        'reason': 'there are no parties with id set'
    }

    result = calculate(item_test_undefined1)
    assert result['result'] is None
    assert result['value'] is None
    assert result['application_count'] is None
    assert result['pass_count'] is None
    assert result['meta'] == {
        'reason': 'there are no values with check-specific properties'
    }

    result = calculate(item_test_undefined2)
    assert result['result'] is None
    assert result['value'] is None
    assert result['application_count'] is None
    assert result['pass_count'] is None
    assert result['meta'] == {
        'reason': 'there are no values with check-specific properties'
    }

    result = calculate(item_test_undefined3)
    assert result['result'] is None
    assert result['value'] is None
    assert result['application_count'] is None
    assert result['pass_count'] is None
    assert result['meta'] == {
        'reason': 'there are no values with check-specific properties'
    }

item_test_passed = {
    'parties': [
        {
            'id': '0',
            'roles': ['payee']
        }
    ],
    'contracts': [
        {
            'implementation': {
                'transactions': [
                    {
                        'payee': {
                            'id': '0'
                        }
                    }
                ]
            }
        }
    ]
}


def test_passed():
    result = calculate(item_test_passed)
    assert result['result'] is True
    assert result['value'] is None
    assert result['application_count'] == 1
    assert result['pass_count'] == 1
    assert result['meta'] == {
        'references': [
            {
                'organization.id': '0',
                'expected_role': 'payee',
                'referenced_party_path': 'parties[0]',
                'referenced_party': item_test_passed['parties'][0],
                'resource_path': 'contracts[0].implementation.transactions[0].payee',
                'resource': item_test_passed['contracts'][0]['implementation']['transactions'][0]['payee'],
                'result': True
            }
        ]
    }

item_test_failed1 = {
    'parties': [
        {
            'id': '0',
            'roles': []
        }
    ],
    'contracts': [
        {
            'implementation': {
                'transactions': [
                    {
                        'payee': {
                            'id': '0'
                        }
                    }
                ]
            }
        }
    ]
}

item_test_failed2 = {
    'parties': [
        {
            'id': '0',
            'roles': ['payee']
        },
        {
            'id': '1'
        },
        {
            'id': '2',
            'roles': ['unknown']
        }
    ],
    'contracts': [
        {
            'implementation': {
                'transactions': [
                    {
                        'payee': {
                            'id': '0'
                        }
                    }
                ]
            }
        },
        {
            'implementation': {
                'transactions': [
                    {
                        'payee': {
                            'id': '1'
                        }
                    },
                    {
                        'payee': {
                            'id': '2'
                        }
                    }
                ]
            }
        }
    ]
}


def test_failed():
    result = calculate(item_test_failed1)
    assert result['result'] is False
    assert result['value'] is None
    assert result['application_count'] == 1
    assert result['pass_count'] == 0
    assert result['meta'] == {
        'references': [
            {
                'organization.id': '0',
                'expected_role': 'payee',
                'referenced_party_path': 'parties[0]',
                'referenced_party': item_test_failed1['parties'][0],
                'resource_path': 'contracts[0].implementation.transactions[0].payee',
                'resource': item_test_failed1['contracts'][0]['implementation']['transactions'][0]['payee'],
                'result': False
            }
        ]
    }

    result = calculate(item_test_failed2)
    assert result['result'] is False
    assert result['value'] is None
    assert result['application_count'] == 3
    assert result['pass_count'] == 1
    assert result['meta'] == {
        'references': [
            {
                'organization.id': '0',
                'expected_role': 'payee',
                'referenced_party_path': 'parties[0]',
                'referenced_party': item_test_failed2['parties'][0],
                'resource_path': 'contracts[0].implementation.transactions[0].payee',
                'resource': item_test_failed2['contracts'][0]['implementation']['transactions'][0]['payee'],
                'result': True
            },
            {
                'organization.id': '1',
                'expected_role': 'payee',
                'referenced_party_path': 'parties[1]',
                'referenced_party': item_test_failed2['parties'][1],
                'resource_path': 'contracts[1].implementation.transactions[0].payee',
                'resource': item_test_failed2['contracts'][1]['implementation']['transactions'][0]['payee'],
                'result': False
            },
            {
                'organization.id': '2',
                'expected_role': 'payee',
                'referenced_party_path': 'parties[2]',
                'referenced_party': item_test_failed2['parties'][2],
                'resource_path': 'contracts[1].implementation.transactions[1].payee',
                'resource': item_test_failed2['contracts'][1]['implementation']['transactions'][1]['payee'],
                'result': False
            }
        ]
    }
