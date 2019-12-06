
from dataset.distribution.code_distribution import CodeDistribution
from tools.helpers import is_subset_dict

items_multiple_items = [
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'a'
            },
            {
                'status': 'a'
            },
            {
                'status': 'b'
            }
        ]
    },
    {
        'ocid': 1,
        'awards': [
            {
                'status': 'b'
            }
        ]
    }
]

items_complex_structure = [
    {
        'ocid': 0,
        'contracts': [
            {
                'implementation': {
                    'milestones': [
                        {
                            'status': 'a'
                        },
                        {
                            'status': 'a'
                        }
                    ]
                }
            },
            {
                'implementation': {
                    'milestones': [
                        {
                            'status': 'b'
                        },
                        {
                            'status': 'b'
                        }
                    ]
                }
            }
        ]
    }
]

items_multiple_paths = [
    {
        'ocid': 0,
        'planning': {
            'documents': [
                {
                    'documentType': 'a'
                }
            ]
        },
        'tender': {
            'documents': [
                {
                    'documentType': 'b'
                }
            ]
        }
    }
]


def test_no_test_values():
    # items_multiple_items
    distribution = CodeDistribution(['awards.status'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_multiple_items:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert is_subset_dict({'share': 0.5, 'count': 2}, result['meta']['shares']['a'])
    assert len(result['meta']['shares']['a']['examples']) == 2
    assert is_subset_dict({'share': 0.5, 'count': 2}, result['meta']['shares']['b'])
    assert len(result['meta']['shares']['b']['examples']) == 2

    # items_complex_structure
    distribution = CodeDistribution(['contracts.implementation.milestones.status'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_complex_structure:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert is_subset_dict({'share': 0.5, 'count': 2}, result['meta']['shares']['a'])
    assert len(result['meta']['shares']['a']['examples']) == 2
    assert is_subset_dict({'share': 0.5, 'count': 2}, result['meta']['shares']['b'])
    assert len(result['meta']['shares']['b']['examples']) == 2

    # items_multiple_paths
    distribution = CodeDistribution(['planning.documents.documentType', 'tender.documents.documentType'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_multiple_paths:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert result['meta'] == {
        'shares': {
            'a': {
                'share': 0.5,
                'count': 1,
                'examples': [{'ocid': 0, 'item_id': 0}]
            },
            'b': {
                'share': 0.5,
                'count': 1,
                'examples': [{'ocid': 0, 'item_id': 0}]
            }
        }
    }


items_passed1 = [
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'a'
            },
            {
                'status': 'b'
            },
            {
                'status': 'c'
            },
            {
                'status': 'd'
            }
        ]
    }
]

items_passed2 = [
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'a'
            }
        ]
    }
]
items_passed2.extend([
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'b'
            }
        ]
    }
    for i in range(999)
])

items_passed3 = [
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'a'
            }
        ]
    }
]
items_passed3.extend([
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'b'
            }
        ]
    }
    for i in range(99)
])


def test_passed():
    # test_passed1
    distribution = CodeDistribution(['awards.status'], ['a', 'b', 'c', 'd'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_passed1:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert result['meta'] == {
        'shares': {
            'a': {
                'share': 1/4,
                'count': 1,
                'examples': [{'ocid': 0, 'item_id': 0}]
            },
            'b': {
                'share': 1/4,
                'count': 1,
                'examples': [{'ocid': 0, 'item_id': 0}]
            },
            'c': {
                'share': 1/4,
                'count': 1,
                'examples': [{'ocid': 0, 'item_id': 0}]
            },
            'd': {
                'share': 1/4,
                'count': 1,
                'examples': [{'ocid': 0, 'item_id': 0}]
            }
        }
    }

    # test_passed2
    distribution = CodeDistribution(['awards.status'], ['a'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_passed2:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert is_subset_dict({'share': 1/1000, 'count': 1}, result['meta']['shares']['a'])
    assert len(result['meta']['shares']['a']['examples']) == 1
    assert is_subset_dict({'share': 999/1000, 'count': 999}, result['meta']['shares']['b'])
    assert len(result['meta']['shares']['b']['examples']) == 20

    # test_passed3
    distribution = CodeDistribution(['awards.status'], ['a', 'b'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_passed3:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert is_subset_dict({'share': 1/100, 'count': 1}, result['meta']['shares']['a'])
    assert len(result['meta']['shares']['a']['examples']) == 1
    assert is_subset_dict({'share': 99/100, 'count': 99}, result['meta']['shares']['b'])
    assert len(result['meta']['shares']['b']['examples']) == 20


items_failed1 = [
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'a'
            }
        ]
    }
]

items_failed2 = [
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'a'
            }
        ]
    }
]

items_failed2.extend([
    {
        'ocid': 0,
        'awards': [
            {
                'status': 'b'
            }
        ]
    }
    for i in range(1000)
])


def test_failed():
    # test_failed1
    distribution = CodeDistribution(['awards.status'], ['a'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_failed1:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is False
    assert result['value'] == 0
    assert result['meta'] == {
        'shares': {
            'a': {
                'share': 1.0,
                'count': 1,
                'examples': [{'ocid': 0, 'item_id': 0}]
            }
        }
    }

    # test_failed2
    distribution = CodeDistribution(['awards.status'], ['a'], samples_cap=20)
    scope = {}
    id = 0
    for item in items_failed2:
        scope = distribution.add_item(scope, item, id)
        id += 1

    result = distribution.get_result(scope)
    assert result['result'] is False
    assert result['value'] == 0
    assert is_subset_dict({'share': 1/1001, 'count': 1}, result['meta']['shares']['a'])
    assert len(result['meta']['shares']['a']['examples']) == 1
    assert is_subset_dict({'share': 1000/1001, 'count': 1000}, result['meta']['shares']['b'])
    assert len(result['meta']['shares']['b']['examples']) == 20



