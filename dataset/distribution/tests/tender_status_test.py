
import random

from dataset.distribution import tender_status

item_test_undefined1 = {
    'tender': {

    }
}

item_test_undefined2 = {
    'tender': {
        'status': None
    }
}

item_test_undefined3 = {
    'tender': {
        'status': 'unknown'
    }
}


def test_undefined():
    scope = {}
    result = tender_status.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'no data items were processed'
    }

    scope = {}
    scope = tender_status.add_item(scope, {}, 0)
    result = tender_status.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there is not a single tender with valid status'
    }

    scope = {}
    scope = tender_status.add_item(scope, item_test_undefined1, 0)
    result = tender_status.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there is not a single tender with valid status'
    }

    scope = {}
    scope = tender_status.add_item(scope, item_test_undefined2, 0)
    result = tender_status.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there is not a single tender with valid status'
    }

    scope = {}
    scope = tender_status.add_item(scope, item_test_undefined3, 0)
    result = tender_status.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there is not a single tender with valid status'
    }

items_test_passed = [
    {
        'tender': {
            'status': 'active'
        }
    },
    {
        'tender': {
            'status': 'planning'
        }
    }
]


def test_passed():
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = tender_status.add_item(scope, item, id)
        id += 1

    result = tender_status.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert len(result['meta']['status']) == len(tender_status.possible_status)
    assert result['meta']['status']['active'] == {
        'share': 0.5,
        'examples_id': [0]
    }
    assert result['meta']['status']['planning'] == {
        'share': 0.5,
        'examples_id': [1]
    }

items_test_failed = [
    {
        'tender': {
            'status': 'active'
        }
    },
    {
        'tender': {
            'status': 'unknown'
        }
    }
]


def test_failed():
    scope = {}

    id = 0
    for item in items_test_failed:
        scope = tender_status.add_item(scope, item, id)
        id += 1

    result = tender_status.get_result(scope)
    assert result['result'] is False
    assert result['value'] == 0
    assert len(result['meta']['status']) == len(tender_status.possible_status)
    assert result['meta']['status']['active'] == {
        'share': 1,
        'examples_id': [0]
    }

items_test_passed_big_load = [
    {
        'tender': {
            'status': random.choice(tender_status.possible_status)
        }
    }
    for _ in range(100000)
]


# following test will pass with high probability
def test_passed_big_load():
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = tender_status.add_item(scope, item, id)
        id += 1

    result = tender_status.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert len(result['meta']['status']) == len(tender_status.possible_status)
    assert sum(
        [len(value['examples_id']) for _, value in result['meta']['status'].items()]
    ) == tender_status.samples_num * len(tender_status.possible_status)
    assert all(
        [0 < value['share'] < 1 for _, value in result['meta']['status'].items()]
    )
