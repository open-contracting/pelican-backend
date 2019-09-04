import random

from dataset.distribution import tender_award_criteria

tender_award_criteria = tender_award_criteria.TenderAwardCriteriaPathClass()

possible_enums = [
    "b", "c", "d", "e", "f"
]


item_test_undefined1 = {
    'ocid': '1',
    'tender': {

    }
}

item_test_undefined2 = {
    'ocid': '2',
    'tender': {
        'awardCriteria': None
    }
}


def test_undefined():
    scope = {}
    result = tender_award_criteria.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'no data items were processed'
    }

    scope = {}
    scope = tender_award_criteria.add_item(scope, {'ocid': '0'}, 0)
    result = tender_award_criteria.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'no data items were processed'
    }

    scope = {}
    scope = tender_award_criteria.add_item(scope, item_test_undefined1, 0)
    result = tender_award_criteria.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'no data items were processed'
    }

    scope = {}
    scope = tender_award_criteria.add_item(scope, item_test_undefined2, 0)
    result = tender_award_criteria.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'no data items were processed'
    }


items_test_passed = [
    {
        'ocid': '0',
        'tender': {
            'awardCriteria': 'a'
        }
    },
    {
        'ocid': '1',
        'tender': {
            'awardCriteria': 'b'
        }
    }
]


def test_passed():
    scope = {}

    id = 0
    for item in items_test_passed:
        scope = tender_award_criteria.add_item(scope, item, id)
        id += 1

    result = tender_award_criteria.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert len(result['meta']['shares']) == len(items_test_passed)
    assert result['meta']['shares']['a'] == {
        'share': 0.5,
        'count': 1,
        'examples': [{'item_id': 0, 'ocid': '0'}]
    }
    assert result['meta']['shares']['b'] == {
        'share': 0.5,
        'count': 1,
        'examples': [{'item_id': 1, 'ocid': '1'}]
    }


items_test_passed_big_load = [
    {
        'ocid': str(i),
        'tender': {
            'awardCriteria': random.choice(possible_enums)
        }
    }
    for i in range(1000)
]


# following test will pass with high probability
def test_passed_big_load():
    scope = {}

    id = 0
    for item in items_test_passed_big_load:
        scope = tender_award_criteria.add_item(scope, item, id)
        id += 1

    result = tender_award_criteria.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100
    assert len(result['meta']['shares']) == len(possible_enums)
    assert sum(
        [len(value['examples'])
         for _, value in result['meta']['shares'].items()]
    ) == tender_award_criteria.samples_number * len(possible_enums)
    assert all(
        [0 < value['share'] < 1 for _, value in result['meta']['shares'].items()]
    )
