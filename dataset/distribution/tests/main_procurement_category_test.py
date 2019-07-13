from dataset.distribution import main_procurement_category


def test_empty():
    scope = {}
    scope = main_procurement_category.add_item(scope, {}, 1)
    scope = main_procurement_category.add_item(scope, {}, 2)
    result = main_procurement_category.get_result(scope)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] is None


first = {
    "tender": {
        "mainProcurementCategory": "A"
    }
}

second = {
    "tender": {
        "mainProcurementCategory": "B"
    }
}

third = {
    "tender": {
        "mainProcurementCategory": "B"
    }
}

fourth = {
    "tender": {
        "mainProcurementCategory": "B"
    }
}


def test_ok():
    scope = {}
    scope = main_procurement_category.add_item(scope, first, 1)
    scope = main_procurement_category.add_item(scope, second, 2)
    scope = main_procurement_category.add_item(scope, third, 3)
    result = main_procurement_category.get_result(scope)
    assert type(result) == dict
    assert result["result"] is True
    assert result["value"] is 100
    assert result["meta"] == {
        "shares": {
            "B": {
                "share": 66,
                "count": 2,
                "examples": [2, 3]
            },
            "A": {
                "share": 33,
                "count": 1,
                "examples": [1]
            },
        }
    }


def test_failed():
    scope = {}
    scope = main_procurement_category.add_item(scope, second, 2)
    scope = main_procurement_category.add_item(scope, third, 3)
    result = main_procurement_category.get_result(scope)
    assert type(result) == dict
    assert result["result"] is False
    assert result["value"] is 0
    assert result["meta"] == {
        "shares": {
            "B": {
                "share": 100,
                "count": 2,
                "examples": [2, 3]
            },
        }
    }
