
import random

from dataset.distribution import \
    tender_value_repetition, \
    awards_value_repetition, \
    contracts_value_repetition


def test_undefined():
    scope = {}
    scope = tender_value_repetition.add_item(scope, {}, 1)
    result = tender_value_repetition.get_result(scope)
    assert result['result'] is None
    assert result['value'] is None
    assert result['meta'] == {
        'reason': ('total count of distinct value.amount and '
                   'value.currency is zero')
    }

item_test_passed = {
    'awards': [
        {
            'value': {'amount': num, 'currency': 'USD'}
        }
        for num in range(31)
    ]
}


def test_passed():
    scope = {}
    scope = awards_value_repetition.add_item(
        scope,
        item_test_passed,
        0
    )
    result = awards_value_repetition.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 3/31
    assert result['meta'] == [[0], [0], [0]]

items_test_passed_multiple = [
    {
        'contracts': [
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
        scope = contracts_value_repetition.add_item(
            scope,
            item,
            id
        )
        id += 1

    result = contracts_value_repetition.get_result(scope)
    assert result['result'] is True
    assert result['value'] == 3/31
    assert result['meta'] == [[0], [1], [2]]

items_test_big_load = [
    {
        'contracts': [
            {
                'value': {
                    'amount': random.randint(1, 100),
                    'currency': random.choice(['USD', 'CZK', 'JPY'])
                }
            }
            for __ in range(random.randint(0, 5))
        ]
    }
    for _ in range(100000)
]


def test_big_load():
    scope = {}

    id = 0
    for item in items_test_big_load:
        scope = contracts_value_repetition.add_item(
            scope,
            item,
            id
        )
        id += 1

    result = contracts_value_repetition.get_result(scope)

    # following asserts will pass with high probability
    assert result['result'] is True
    assert len(result['meta']) == 3
    assert sum([len(el) for el in result['meta']]) == 30
