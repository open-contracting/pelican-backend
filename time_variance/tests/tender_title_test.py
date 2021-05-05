from time_variance import tender_title
from tools.checks import get_empty_result_time_variance_scope

ancestor = {"ocid": "2", "tender": {"title": "Title 1"}}

new_item = {"ocid": "2", "tender": {"title": "title  1"}}


def test_evaluate():
    scope = get_empty_result_time_variance_scope()
    scope, result = tender_title.evaluate(scope, ancestor, 1, None, None)
    assert result == False

    scope, result = tender_title.evaluate(scope, ancestor, 1, new_item, 3)
    assert result == True


ancestor_no_title_1 = {"ocid": "3", "tender": {}}


ancestor_no_title_2 = {
    "ocid": "4",
}


ancestor_no_title_3 = {"ocid": "3", "tender": {"title": ""}}


ancestor_title_1 = {"ocid": "4", "tender": {"title": "titel"}}


def test_filter():
    scope = get_empty_result_time_variance_scope()
    assert False == tender_title.filter(scope, ancestor_no_title_1, 1, None, None)
    assert False == tender_title.filter(scope, ancestor_no_title_2, 1, None, None)
    assert False == tender_title.filter(scope, ancestor_no_title_3, 1, None, None)
    assert True == tender_title.filter(scope, ancestor_title_1, 1, None, None)
