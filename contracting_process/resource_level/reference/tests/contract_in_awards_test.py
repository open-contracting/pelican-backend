from contracting_process.resource_level.reference.contract_in_awards import calculate


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "insufficient data for check"}


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


item_failed = {
    "contracts": [
        {"dateSigned": "2015-12-31T00:00:00Z", "awardID": "1"},
        {"dateSigned": "2017-12-31T00:00:00Z", "awardID": "2"},
        {"dateSigned": "2017-12-31T00:00:00Z", "awardID": "3"},
        {"dateSigned": "2017-12-31T00:00:00Z"},
    ],
    "awards": [
        {"date": "2015-12-30T00:00:00Z", "id": "1"},
        {"date": "2017-12-30T00:00:00Z", "id": "2"},
        {"date": "2017-12-30T00:00:00Z", "id": "2"},
    ],
}


def test_failed():
    result = calculate(item_failed)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 4
    assert result["pass_count"] == 1
    assert result["meta"] == {"failed_paths": ["contracts[1]", "contracts[2]", "contracts[3]"]}
