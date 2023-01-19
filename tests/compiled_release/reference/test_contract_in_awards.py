from contracting_process.resource_level.reference.contract_in_awards import calculate


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "no contract is set"}


item_ok = {
    "contracts": [
        {"dateSigned": "2015-12-31T00:00:00Z", "awardID": "1"},
        {"dateSigned": "2017-12-31T00:00:00Z", "awardID": "2"},
    ],
    "awards": [{"date": "2015-12-30T00:00:00Z", "id": "1"}, {"date": "2017-12-30T00:00:00Z", "id": "2"}],
}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 2
    assert result["pass_count"] == 2
    assert result["meta"] is None


item_failed1 = {
    "contracts": [
        {"dateSigned": "2015-12-31T00:00:00Z", "awardID": "1"},
        {"dateSigned": "2017-12-31T00:00:00Z", "awardID": "2"},
        {"dateSigned": "2017-12-31T00:00:00Z", "awardID": "3"},
        {"dateSigned": "2017-12-31T00:00:00Z"},
    ],
    "awards": [
        {"date": "2015-12-30T00:00:00Z", "id": "1"},
        {"date": "2017-12-30T00:00:00Z", "id": "2"},
        {"date": "2017-12-30T00:00:00Z", "id": "2", "title": ""},
    ],
}

item_failed2 = {
    "contracts": [
        {"dateSigned": "2015-12-31T00:00:00Z", "awardID": "1"},
    ],
}


def test_failed():
    result = calculate(item_failed1)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 4
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "failed_paths": [
            {"path": "contracts[1]", "reason": "multiple awards match the awardID"},
            {"path": "contracts[2]", "reason": "no award matches the awardID"},
            {"path": "contracts[3]", "reason": "contract has no awardID"},
        ]
    }

    result = calculate(item_failed2)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {"path": "contracts[0]", "reason": "no award matches the awardID"},
        ]
    }
