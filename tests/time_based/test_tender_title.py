from pelican.util.checks import get_empty_result_time_based_scope
from time_variance.checks import tender_title

ancestor = {"ocid": "2", "tender": {"title": "Title 1"}}

new_item = {"ocid": "2", "tender": {"title": "title  1"}}


def test_evaluate():
    scope = get_empty_result_time_based_scope()
    scope, result = tender_title.evaluate(scope, ancestor, 1, None, None)
    assert result is False

    scope, result = tender_title.evaluate(scope, ancestor, 1, new_item, 3)
    assert result is True


ancestor_no_title_1 = {"ocid": "3", "tender": {}}


ancestor_no_title_2 = {
    "ocid": "4",
}


ancestor_no_title_3 = {"ocid": "3", "tender": {"title": ""}}


ancestor_title_1 = {"ocid": "4", "tender": {"title": "title"}}


def test_applicable():
    scope = get_empty_result_time_based_scope()
    assert tender_title.applicable(scope, ancestor_no_title_1, 1, None, None) is False
    assert tender_title.applicable(scope, ancestor_no_title_2, 1, None, None) is False
    assert tender_title.applicable(scope, ancestor_no_title_3, 1, None, None) is False
    assert tender_title.applicable(scope, ancestor_title_1, 1, None, None) is True
