
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
                'path': 'f'
            }
        ]
    }
