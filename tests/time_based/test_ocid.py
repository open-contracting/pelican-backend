from pelican.util.checks import get_empty_result_time_based_scope
from time_variance.checks import ocid

ancestor = {
    "ocid": "2",
}

new_item = {
    "ocid": "3",
}


def test_applicable():
    scope = get_empty_result_time_based_scope()
    result = ocid.applicable(scope, ancestor, 1, new_item, 1024)
    assert result is True

    result = ocid.applicable(scope, ancestor, 1, None, None)
    assert result is True


ok_ancestor = {
    "ocid": "3",
}


def test_evaluate():
    scope = get_empty_result_time_based_scope()
    scope, result = ocid.evaluate(scope, ancestor, 1, None, None)
    assert result is False

    scope, result = ocid.evaluate(scope, ok_ancestor, 1, new_item, 12)
    assert result is True
