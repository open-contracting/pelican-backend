from time_variance import ocid
from tools.checks import get_empty_result_time_variance_scope

ancestor = {
    'ocid': '2',
}

new_item = {
    'ocid': '3',
}


def test_filter():
    scope = get_empty_result_time_variance_scope()
    result = ocid.filter(scope, ancestor, 1, new_item, 1024)
    assert result == True

    result = ocid.filter(scope, ancestor, 1, None, None)
    assert result == True


ok_ancestor = {
    'ocid': '3',
}


def test_evaluate():
    scope = get_empty_result_time_variance_scope()
    scope, result = ocid.evaluate(scope, ancestor, 1, None, None)
    assert result == False

    scope, result = ocid.evaluate(scope, ok_ancestor, 1, new_item, 12)
    assert result == True
