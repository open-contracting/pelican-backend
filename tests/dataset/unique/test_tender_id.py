from dataset.unique import tender_id


def test_undefined():
    scope = {}
    scope = tender_id.add_item(scope, {"ocid": "1"}, 1)
    scope = tender_id.add_item(scope, {"ocid": "2", "tender": {}}, 2)
    result = tender_id.get_result(scope)

    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "there are no tenders with check-specific properties"}


def test_passed():
    scope = {}
    scope = tender_id.add_item(scope, {"ocid": "1", "tender": {"id": 1}}, 1)
    scope = tender_id.add_item(scope, {"ocid": "2", "tender": {"id": "2"}}, 2)
    scope = tender_id.add_item(scope, {"ocid": "3"}, 3)
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
    scope = tender_id.add_item(scope, {"ocid": "1", "tender": {"id": 1}}, 1)
    scope = tender_id.add_item(scope, {"ocid": "2", "tender": {"id": 1}}, 2)
    scope = tender_id.add_item(scope, {"ocid": "3", "tender": {"id": 3}}, 3)
    scope = tender_id.add_item(scope, {"ocid": "4", "tender": {"id": 4}}, 4)
    scope = tender_id.add_item(scope, {"ocid": "5"}, 5)
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