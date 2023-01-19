from contracting_process.resource_level.coherent.amendments_dates import calculate


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "no pairs of dates are set"}


item_ok = {
    "date": "2019-12-31T00:00:00Z",
    "tender": {
        "tenderPeriod": {"startDate": "2014-12-31T00:00:00Z"},
        "amendments": [{"date": "2015-12-31T00:00:00Z"}, {"date": "2015-12-31T00:00:00Z"}],
    },
    "awards": [
        {"date": "2014-12-31T00:00:00Z"},
        {
            "date": "2014-12-31T00:00:00Z",
            "amendments": [{"date": "2015-12-31T00:00:00Z"}, {"date": "2015-12-31T00:00:00Z"}],
        },
    ],
    "contracts": [{"dateSigned": "2014-12-31T00:00:00Z", "amendments": [{"date": "2015-12-31T00:00:00Z"}]}],
}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 10
    assert result["pass_count"] == 10
    assert result["meta"] is None


item_failed = {
    "date": "2000-12-31T00:00:00Z",
    "tender": {
        "tenderPeriod": {"startDate": "2020-12-31T00:00:00Z"},
        "amendments": [{"date": "2015-12-31T00:00:00Z"}, {"date": "2015-12-31T00:00:00Z"}],
    },
    "awards": [
        {"date": "2020-12-31T00:00:00Z"},
        {
            "date": "2020-12-31T00:00:00Z",
            "amendments": [{"date": "2015-12-31T00:00:00Z"}, {"date": "2015-12-31T00:00:00Z"}],
        },
    ],
    "contracts": [{"dateSigned": "2020-12-31T00:00:00Z", "amendments": [{"date": "2015-12-31T00:00:00Z"}]}],
}


def test_failed():
    result = calculate(item_failed)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 10
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {
                "path_1": "tender.tenderPeriod.startDate",
                "path_2": "tender.amendments[0].date",
                "value_1": "2020-12-31T00:00:00Z",
                "value_2": "2015-12-31T00:00:00Z",
            },
            {
                "path_1": "tender.tenderPeriod.startDate",
                "path_2": "tender.amendments[1].date",
                "value_1": "2020-12-31T00:00:00Z",
                "value_2": "2015-12-31T00:00:00Z",
            },
            {
                "path_1": "awards[1].date",
                "path_2": "awards[1].amendments[0].date",
                "value_1": "2020-12-31T00:00:00Z",
                "value_2": "2015-12-31T00:00:00Z",
            },
            {
                "path_1": "awards[1].date",
                "path_2": "awards[1].amendments[1].date",
                "value_1": "2020-12-31T00:00:00Z",
                "value_2": "2015-12-31T00:00:00Z",
            },
            {
                "path_1": "contracts[0].dateSigned",
                "path_2": "contracts[0].amendments[0].date",
                "value_1": "2020-12-31T00:00:00Z",
                "value_2": "2015-12-31T00:00:00Z",
            },
            {
                "path_1": "tender.amendments[0].date",
                "path_2": "date",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
            {
                "path_1": "tender.amendments[1].date",
                "path_2": "date",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
            {
                "path_1": "awards[1].amendments[0].date",
                "path_2": "date",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
            {
                "path_1": "awards[1].amendments[1].date",
                "path_2": "date",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
            {
                "path_1": "contracts[0].amendments[0].date",
                "path_2": "date",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
        ]
    }
