from dataset.distribution import main_procurement_category

item_unset1 = {"ocid": "1"}
item_unset2 = {"ocid": "2"}


def test_empty():
    scope = {}
    scope = main_procurement_category.add_item(scope, item_unset1, 1)
    scope = main_procurement_category.add_item(scope, item_unset2, 2)
    result = main_procurement_category.get_result(scope)
    assert type(result) is dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] is None


first = {"ocid": "1", "tender": {"mainProcurementCategory": "goods"}}

second = {"ocid": "2", "tender": {"mainProcurementCategory": "works"}}

third = {"ocid": "3", "tender": {"mainProcurementCategory": "works"}}

fourth = {"ocid": "4", "tender": {"mainProcurementCategory": "works"}}


def test_ok():
    scope = {}
    scope = main_procurement_category.add_item(scope, first, 1)
    scope = main_procurement_category.add_item(scope, second, 2)
    scope = main_procurement_category.add_item(scope, third, 3)
    result = main_procurement_category.get_result(scope)
    assert type(result) is dict
    assert result["result"] is True
    assert result["value"] == 100
    assert result["meta"] == {
        "shares": {
            "works": {
                "share": 2 / 3,
                "count": 2,
                "examples": [{"item_id": 2, "ocid": "2"}, {"item_id": 3, "ocid": "3"}],
            },
            "goods": {"share": 1 / 3, "count": 1, "examples": [{"item_id": 1, "ocid": "1"}]},
        }
    }
    assert list(result["meta"]["shares"]) == ["goods", "works"]


def test_failed():
    scope = {}
    scope = main_procurement_category.add_item(scope, second, 2)
    scope = main_procurement_category.add_item(scope, third, 3)
    result = main_procurement_category.get_result(scope)
    assert type(result) is dict
    assert result["result"] is False
    assert result["value"] == 0
    assert result["meta"] == {
        "shares": {
            "works": {
                "share": 1.0,
                "count": 2,
                "examples": [{"item_id": 2, "ocid": "2"}, {"item_id": 3, "ocid": "3"}],
            },
        }
    }
