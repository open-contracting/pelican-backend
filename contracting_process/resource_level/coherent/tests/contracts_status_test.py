
from contracting_process.resource_level.coherent.contracts_status \
    import calculate


item_test_undefined = {
    'contracts': [
        {

        },
        {
            'status': None
        },
        {
            'status': 'active'
        },
        {
            'status': 'terminated'
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
        'reason': 'there are no contracts with check-specific properties'
    }

    result = calculate(item_test_undefined)
    assert result['result'] is None
    assert result['value'] is None
    assert result['application_count'] is None
    assert result['pass_count'] is None
    assert result['meta'] == {
        'reason': 'there are no contracts with check-specific properties'
    }

item_test_passed = {
    'contracts': [
        {

        },
        {
            'status': 'pending'
        },
        {
            'status': 'cancelled',
            'implementation': {

            }
        },
        {
            'status': 'pending',
            'implementation': {
                'transactions': []
            }
        }
    ]
}


def test_passed():
    result = calculate(item_test_passed)
    assert result['result'] is True
    assert result['value'] is None
    assert result['application_count'] == 3
    assert result['pass_count'] == 3
    assert result['meta'] == {
        'processed_contracts': [
            {
                'path': 'contracts[1]',
                'transactions_length': 0,
                'result': True
            },
            {
                'path': 'contracts[2]',
                'transactions_length': 0,
                'result': True
            },
            {
                'path': 'contracts[3]',
                'transactions_length': 0,
                'result': True
            }
        ]
    }

item_test_failed1 = {
    'contracts': [
        {
            'status': 'pending',
            'implementation': {
                'transactions': [
                    {'id': 0}
                ]
            }
        }
    ]
}

item_test_failed2 = {
    'contracts': [
        {

        },
        {
            'status': 'pending',
            'implementation': {
                'transactions': []
            }
        },
        {
            'status': 'cancelled',
            'implementation': {
                'transactions': [
                    {'id': 0},
                    {'id': 1}
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
        'processed_contracts': [
            {
                'path': 'contracts[0]',
                'transactions_length': 1,
                'result': False
            }
        ]
    }

    result = calculate(item_test_failed2)
    assert result['result'] is False
    assert result['value'] is None
    assert result['application_count'] == 2
    assert result['pass_count'] == 1
    assert result['meta'] == {
        'processed_contracts': [
            {
                'path': 'contracts[1]',
                'transactions_length': 0,
                'result': True
            },
            {
                'path': 'contracts[2]',
                'transactions_length': 2,
                'result': False
            }
        ]
    }
