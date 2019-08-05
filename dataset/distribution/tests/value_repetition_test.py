
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
