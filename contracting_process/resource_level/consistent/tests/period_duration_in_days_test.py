
from contracting_process.resource_level.consistent.period_duration_in_days import calculate

item_test_undefined = {
    'tender': {
        'tenderPeriod': {
            'startDate': '2019-08-14T16:47:36+01:00'
        },
        'enquiryPeriod': {
            'startDate': '2019-08-14T16:47:36+01:00',
            'endDate': None,
            'durationInDays': 2
        }
    }
}


def test_undefined():
    result = calculate({})
    assert result['result'] is None
    assert result['application_count'] is None
    assert result['pass_count'] is None
    assert result['meta'] == {'reason': 'there are no values with check-specific properties'}

    result = calculate(item_test_undefined)
    assert result['result'] is None
    assert result['application_count'] is None
    assert result['pass_count'] is None
    assert result['meta'] == {'reason': 'there are no values with check-specific properties'}

item_test_passed1 = {
    'awards': [
        {
            'contractPeriod': {
                'startDate': '2019-08-14T16:47:36+01:00',
                'endDate': None,
                'maxExtentDate': '2019-08-15T16:47:36+01:00',
                'durationInDays': 1
            }
        }
    ],
    'contracts': [
        {
            'period': {
                'startDate': '2019-12-31T16:47:36+01:00',
                'endDate': '2020-01-02T16:47:36+01:00',
                'durationInDays': 2
            }
        },
        {
            'period': {
                'startDate': '2019-01-01T16:47:36+01:00',
                'endDate': '2019-02-01T16:47:36+01:00',
                'durationInDays': 31
            }
        }
    ]
}

item_test_passed2 = {
    'tender': {
        'enquiryPeriod': {
            'startDate': '2019-08-14T16:47:36+01:00',
            'endDate': '2019-08-24T00:00:00+01:00',
            'durationInDays': 10
        }
    }
}


def test_passed():
    result = calculate(item_test_passed1)
    assert result['result'] is True
    assert result['application_count'] == 3
    assert result['pass_count'] == 3
    assert result['meta'] == {
        'periods': [
            {
                'path': 'awards[0].contractPeriod',
                'result': True
            },
            {
                'path': 'contracts[0].period',
                'result': True
            },
            {
                'path': 'contracts[1].period',
                'result': True
            }
        ]
    }

    result = calculate(item_test_passed2)
    assert result['result'] is True
    assert result['application_count'] == 1
    assert result['pass_count'] == 1
    assert result['meta'] == {
        'periods': [
            {
                'path': 'tender.enquiryPeriod',
                'result': True
            }
        ]
    }

item_test_failed = {
    'awards': [
        {
            'contractPeriod': {
                'startDate': '2019-08-14T16:47:36+01:00',
                'endDate': '2019-08-14T16:47:36+01:00',
                'durationInDays': 1
            }
        }
    ],
    'contracts': [
        {
            'period': {
                'startDate': '2019-12-31T16:47:36+01:00',
                'endDate': '2020-01-01T16:47:36+01:00',
                'maxExtentDate': '2020-01-01T16:47:36+01:00',
                'durationInDays': 2
            }
        },
        {
            'period': {
                'startDate': '2019-01-01T16:47:36+01:00',
                'maxExtentDate': '2019-02-01T16:47:36+01:00',
                'durationInDays': 31
            }
        }
    ]
}


def test_failed():
    result = calculate(item_test_failed)
    assert result['result'] is False
    assert result['application_count'] == 3
    assert result['pass_count'] == 1
    assert result['meta'] == {
        'periods': [
            {
                'path': 'awards[0].contractPeriod',
                'result': False
            },
            {
                'path': 'contracts[0].period',
                'result': False
            },
            {
                'path': 'contracts[1].period',
                'result': True
            }
        ]
    }
