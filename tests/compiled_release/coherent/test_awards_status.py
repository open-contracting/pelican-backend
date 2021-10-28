from contracting_process.resource_level.coherent.awards_status import calculate

item_test_undefined = {"awards": [{}, {"status": None}, {"status": "active"}]}


def test_undefined():
    result = calculate({})
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no awards with check-specific properties"}

    result = calculate(item_test_undefined)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no awards with check-specific properties"}


item_test_passed1 = {"awards": [{"status": "pending", "id": 0}]}

item_test_passed2 = {"awards": [{"status": "pending", "id": 0}], "contracts": [{"awardID": 1}]}

item_test_passed3 = {
    "awards": [{"status": "pending", "id": 0}, {"status": "pending", "id": 1}],
    "contracts": [{"awardID": 2}, {"awardID": 3}],
}


def test_passed():
    result = calculate(item_test_passed1)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {"processed_awards": [{"path": "awards[0]", "id": 0, "result": True}]}

    result = calculate(item_test_passed2)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {"processed_awards": [{"path": "awards[0]", "id": 0, "result": True}]}

    result = calculate(item_test_passed3)
    assert result["result"] is True
    assert result["application_count"] == 2
    assert result["pass_count"] == 2
    assert result["meta"] == {
        "processed_awards": [
            {"path": "awards[0]", "id": 0, "result": True},
            {"path": "awards[1]", "id": 1, "result": True},
        ]
    }


item_test_failed1 = {"awards": [{"status": "pending", "id": 0}], "contracts": [{"awardID": 0}]}

item_test_failed2 = {
    "awards": [{"status": "pending", "id": 0}, {"status": "pending", "id": 1}],
    "contracts": [{"awardID": 1}, {"awardID": 2}],
}


def test_failed():
    result = calculate(item_test_failed1)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"processed_awards": [{"path": "awards[0]", "id": 0, "result": False}]}

    result = calculate(item_test_failed2)
    assert result["result"] is False
    assert result["application_count"] == 2
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "processed_awards": [
            {"path": "awards[0]", "id": 0, "result": True},
            {"path": "awards[1]", "id": 1, "result": False},
        ]
    }
