from dataset.misc import url_availability

item_test_undefined = {
    'ocid': '0',
    'planning': {
        'documents': [{
            'url': 'https://www.google.com/'
        }]
    }
}


def test_undefined():
    scope = {}
    scope = url_availability.add_item(scope, {'ocid': '0'}, 0)
    result = url_availability.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there is less than {} URLs in the dataset'
        .format(url_availability.samples_num)
    }

    scope = {}
    scope = url_availability.add_item(scope, item_test_undefined, 0)
    result = url_availability.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there is less than {} URLs in the dataset'
        .format(url_availability.samples_num)
    }

item_test_passed = {
    'ocid': '0',
    'planning': {
        'documents': [
            {
                'url': 'https://www.google.com/'
            }
            for _ in range(25)
        ]
    },
    'tender': {
        'documents': [
            {
                'url': 'https://www.google.com/'
            }
            for _ in range(25)
        ]
    },
    'awards': [
        {
            'documents': [{
                    'url': 'https://www.google.com/'
            }]
        }
        for _ in range(25)
    ],
    'contracts': [
        {
            'documents': [{
                    'url': 'https://www.google.com/'
            }]
        }
        for _ in range(25)
    ]
}


# working when samples_num is set to 100
def test_passed():
    scope = {}
    scope = url_availability.add_item(scope, item_test_passed, 0)
    result = url_availability.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert len(result['meta']['passed_examples']) == 100
    assert len(result['meta']['failed_examples']) == 0
    assert all(
        [s['status'] == 'OK' for s in result['meta']['passed_examples']]
    )

items_test_failed_multiple = [
    {
        'ocid': str(num),
        'planning': {
            'documents': [{
                'url': 'https://www.google.com/'
            }]
        }
    }
    for num in range(99)
]
items_test_failed_multiple.append(
    {
        'ocid': '99',
        'planning': {
            'documents': [{
                'url': 'https://www.nonexistingurl.com/'
            }]
        }
    }
)


# working when samples_num is set to 100
def test_failed_multiple():
    scope = {}

    id = 0
    for item in items_test_failed_multiple:
        scope = url_availability.add_item(
            scope,
            item,
            id
        )
        id += 1

    result = url_availability.get_result(scope)
    assert result['result'] is False
    assert result['value'] == 99
    assert len(result['meta']['passed_examples']) == 99
    assert len(result['meta']['failed_examples']) == 1
    assert len(
        [s for s in result['meta']['passed_examples']
            if s['status'] == 'OK']
    ) == 99
    assert len(
        [s for s in result['meta']['failed_examples']
            if s['status'] == 'ERROR']
    ) == 1
