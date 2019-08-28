
import random

from dataset.distribution import value_repetition
tender_value_repetition = value_repetition.ModuleType('tender')


def test_undefined():
    scope = {}
    scope = tender_value_repetition.add_item(scope, {'ocid': '1'}, 1)
    result = tender_value_repetition.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': 'there are is no suitable data item for this check'
    }

items_test_passed_multiple = [
    {
        'ocid': str(num),
        'tender': [
            {
                'value': {'amount': num, 'currency': 'USD'}
            }
        ]
    }
    for num in range(31)
]


def test_passed_multiple():
    scope = {}

    id = 0
    for item in items_test_passed_multiple:
        scope = tender_value_repetition.add_item(
            scope,
            item,
            id
        )
        id += 1

    result = tender_value_repetition.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 100 * (3 / 31)
    assert len(result['meta']['most_frequent']) == value_repetition.most_frequent_cap
    assert sum(
        [len(el['examples']) for el in result['meta']['most_frequent']]
    ) == value_repetition.most_frequent_cap

items_test_big_load = [
    {
        'ocid': str(i),
        'tender': {
            'value': {
                'amount': random.randint(1, 100),
                'currency': random.choice(['USD', 'CZK', 'JPY'])
            }
        }
    }
    for i in range(300000)
]


def test_big_load():
    scope = {}

    id = 0
    for item in items_test_big_load:
        scope = tender_value_repetition.add_item(
            scope,
            item,
            id
        )
        id += 1

    result = tender_value_repetition.get_result(scope)

    # following asserts will pass with high probability
    assert result['result'] is True
    assert len(result['meta']['most_frequent']) == value_repetition.most_frequent_cap
    assert sum(
        [len(el['examples']) for el in result['meta']['most_frequent']]
    ) == 50
