from contracting_process.resource_level.coherent.dates import calculate


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "insufficient data for check"}


item_ok = {
    "date": "2019-12-31T00:00:00Z",
    "tender": {
        "tenderPeriod": {
            "endDate": "2014-12-31T00:00:00Z"
        },
        "contractPeriod": {
            "startDate": "2015-12-31T00:00:00Z"
        }
    },
    "contracts": [
        {"dateSigned": "2015-12-31T00:00:00Z"},
        {"dateSigned": "2017-12-31T00:00:00Z"}
    ],
    "awards": [
        {"date": "2015-12-30T00:00:00Z"},
        {"date": "2017-12-30T00:00:00Z"}
    ]
}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] is 12
    assert result["pass_count"] is 12
    assert result["meta"] is None
