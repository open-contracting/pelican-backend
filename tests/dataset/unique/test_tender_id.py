from dataset.unique import tender_id

item_tender_unset = {"ocid": "1"}
item_tender_unset3 = {"ocid": "3"}
item_tender_unset5 = {"ocid": "5"}
item_tender_empty = {"ocid": "2", "tender": {}}
item_tender_id_str = {"ocid": "2", "tender": {"id": "2"}}
item_tender_id_int = {"ocid": "1", "tender": {"id": 1}}
item_tender_id_int2 = {"ocid": "2", "tender": {"id": 1}}
item_tender_id_int3 = {"ocid": "3", "tender": {"id": 3}}
item_tender_id_int4 = {"ocid": "4", "tender": {"id": 4}}


def test_undefined():
    scope = {}
    scope = tender_id.add_item(scope, item_tender_unset, 1)
    scope = tender_id.add_item(scope, item_tender_empty, 2)
    result = tender_id.get_result(scope)

    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}


def test_passed():
    scope = {}
    scope = tender_id.add_item(scope, item_tender_id_int, 1)
    scope = tender_id.add_item(scope, item_tender_id_str, 2)
    scope = tender_id.add_item(scope, item_tender_unset3, 3)
    result = tender_id.get_result(scope)

    assert result["result"] is True
    assert result["value"] == 100.0
    assert result["meta"]["passed_examples"] == [
        {
            "tender_id": "1",
            "item_id": 1,
            "ocid": "1",
            "all_items": [{"ocid": "1", "item_id": 1}],
        },
        {
            "tender_id": "2",
            "item_id": 2,
            "ocid": "2",
            "all_items": [{"ocid": "2", "item_id": 2}],
        },
    ]
    assert result["meta"]["failed_examples"] == []
    assert result["meta"]["total_processed"] == 2
    assert result["meta"]["total_passed"] == 2
    assert result["meta"]["total_failed"] == 0


def test_failed():
    scope = {}
    scope = tender_id.add_item(scope, item_tender_id_int, 1)
    scope = tender_id.add_item(scope, item_tender_id_int2, 2)
    scope = tender_id.add_item(scope, item_tender_id_int3, 3)
    scope = tender_id.add_item(scope, item_tender_id_int4, 4)
    scope = tender_id.add_item(scope, item_tender_unset5, 5)
    result = tender_id.get_result(scope)

    assert result["result"] is False
    assert result["value"] == 50.0
    assert len(result["meta"]["failed_examples"]) == 1
    assert result["meta"]["failed_examples"][0]["tender_id"] == "1"
    assert len(result["meta"]["failed_examples"][0]["all_items"]) == 2
    assert result["meta"]["total_processed"] == 4
    assert result["meta"]["total_passed"] == 2
    assert result["meta"]["total_failed"] == 2

    scope = {}
    for i in range(101):
        scope = tender_id.add_item(scope, {"ocid": i, "tender": {"id": 1}}, i)
    result = tender_id.get_result(scope)

    assert result["result"] is False
    assert result["value"] == 0.0
    assert len(result["meta"]["failed_examples"]) == 1
    assert result["meta"]["failed_examples"][0]["tender_id"] == "1"
    assert len(result["meta"]["failed_examples"][0]["all_items"]) == 101
    assert result["meta"]["total_processed"] == 101
    assert result["meta"]["total_passed"] == 0
    assert result["meta"]["total_failed"] == 101
