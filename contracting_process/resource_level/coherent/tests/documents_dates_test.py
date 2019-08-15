
from contracting_process.resource_level.coherent.documents_dates import calculate


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result['result'] is None
    assert empty_result['application_count'] is None
    assert empty_result['pass_count'] is None
    assert empty_result['meta'] == {'reason': 'insufficient data for check'}


item_ok = {
    'date': '2019-12-31T00:00:00Z',
    'planning': {
        'documents': [
            {
                'datePublished': '2014-12-31T00:00:00Z',
                'dateModified': '2015-12-31T00:00:00Z',
            },
            {
                'datePublished': '2014-12-31T00:00:00Z',
                'dateModified': '2015-12-31T00:00:00Z',
            }
        ]
    },
    'tender': {
        'documents': [
            {
                'datePublished': '2014-12-31T00:00:00Z',
                'dateModified': '2015-12-31T00:00:00Z',
            }
        ]
    },
    'awards': [
        {
            'documents': [
                {
                    'datePublished': '2014-12-31T00:00:00Z',
                    'dateModified': '2015-12-31T00:00:00Z',
                }
            ]
        }
    ],
    'contracts': [
        {
            'documents': [
                {
                    'datePublished': '2014-12-31T00:00:00Z',
                    'dateModified': '2015-12-31T00:00:00Z',
                }
            ]
        },
        {
            'implementation': {
                'documents': [
                    {
                        'datePublished': '2014-12-31T00:00:00Z',
                        'dateModified': '2015-12-31T00:00:00Z',
                    }
                ]
            }
        },
        {
            'milestones': [
                {
                    'documents': [
                        {
                            'datePublished': '2014-12-31T00:00:00Z',
                            'dateModified': '2015-12-31T00:00:00Z',
                        }
                    ]
                }
            ]
        }
    ]
}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result['result'] is True
    assert result['application_count'] == 21
    assert result['pass_count'] == 21
    assert result['meta'] is None


item_failed = {
    'date': '2010-12-31T00:00:00Z',
    'planning': {
        'documents': [
            {
                'datePublished': '2030-12-31T00:00:00Z',
                'dateModified': '2020-12-31T00:00:00Z',
            },
            {
                'datePublished': '2030-12-31T00:00:00Z',
                'dateModified': '2020-12-31T00:00:00Z',
            }
        ]
    },
    'tender': {
        'documents': [
            {
                'datePublished': '2030-12-31T00:00:00Z',
                'dateModified': '2020-12-31T00:00:00Z',
            }
        ]
    },
    'awards': [
        {
            'documents': [
                {
                    'datePublished': '2030-12-31T00:00:00Z',
                    'dateModified': '2020-12-31T00:00:00Z',
                }
            ]
        }
    ],
    'contracts': [
        {
            'documents': [
                {
                    'datePublished': '2030-12-31T00:00:00Z',
                    'dateModified': '2020-12-31T00:00:00Z',
                }
            ]
        },
        {
            'implementation': {
                'documents': [
                    {
                        'datePublished': '2030-12-31T00:00:00Z',
                        'dateModified': '2020-12-31T00:00:00Z',
                    }
                ]
            }
        },
        {
            'milestones': [
                {
                    'documents': [
                        {
                            'datePublished': '2030-12-31T00:00:00Z',
                            'dateModified': '2020-12-31T00:00:00Z',
                        }
                    ]
                }
            ]
        }
    ]
}


def test_failed():
    result = calculate(item_failed)
    assert type(result) == dict
    assert result['result'] is False
    assert result['application_count'] == 21
    assert result['pass_count'] == 0
    assert result['meta'] == {'failed_paths': [
        {
            'path_1': 'planning.documents[0].datePublished', 'path_2': 'planning.documents[0].dateModified',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2020-12-31T00:00:00Z'
        }, {
            'path_1': 'planning.documents[0].datePublished', 'path_2': 'date',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'planning.documents[0].dateModified', 'path_2': 'date',
            'value_1': '2020-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'planning.documents[1].datePublished', 'path_2': 'planning.documents[1].dateModified',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2020-12-31T00:00:00Z'
        }, {
            'path_1': 'planning.documents[1].datePublished', 'path_2': 'date',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'planning.documents[1].dateModified', 'path_2': 'date',
            'value_1': '2020-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'tender.documents[0].datePublished', 'path_2': 'tender.documents[0].dateModified',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2020-12-31T00:00:00Z'
        }, {
            'path_1': 'tender.documents[0].datePublished', 'path_2': 'date',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'tender.documents[0].dateModified', 'path_2': 'date',
            'value_1': '2020-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'awards[0].documents[0].datePublished', 'path_2': 'awards[0].documents[0].dateModified',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2020-12-31T00:00:00Z'
        }, {
            'path_1': 'awards[0].documents[0].datePublished', 'path_2': 'date',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'awards[0].documents[0].dateModified', 'path_2': 'date',
            'value_1': '2020-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[0].documents[0].datePublished', 'path_2': 'contracts[0].documents[0].dateModified',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2020-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[0].documents[0].datePublished', 'path_2': 'date',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[0].documents[0].dateModified', 'path_2': 'date',
            'value_1': '2020-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[1].implementation.documents[0].datePublished', 'path_2': 'contracts[1].implementation.documents[0].dateModified',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2020-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[1].implementation.documents[0].datePublished', 'path_2': 'date',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[1].implementation.documents[0].dateModified', 'path_2': 'date',
            'value_1': '2020-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[2].milestones[0].documents[0].datePublished', 'path_2': 'contracts[2].milestones[0].documents[0].dateModified',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2020-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[2].milestones[0].documents[0].datePublished', 'path_2': 'date',
            'value_1': '2030-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }, {
            'path_1': 'contracts[2].milestones[0].documents[0].dateModified', 'path_2': 'date',
            'value_1': '2020-12-31T00:00:00Z', 'value_2': '2010-12-31T00:00:00Z'
        }
    ]}
