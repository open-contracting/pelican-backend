from contracting_process.resource_level.coherent.dates import calculate

item_special_case = {  # tender.tenderPeriod.endDate > date
    "date": "2019-12-31T00:00:00Z",
    "tender": {"tenderPeriod": {"endDate": "2020-12-31T00:00:00Z"}},
}


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) is dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "no pairs of dates are set"}
    empty_result2 = calculate(item_special_case)
    assert type(empty_result2) is dict
    assert empty_result2["result"] is None
    assert empty_result2["application_count"] is None
    assert empty_result2["pass_count"] is None
    assert empty_result2["meta"] == {"reason": "no pairs of dates are set"}


item_ok = {
    "date": "2019-12-31T00:00:00Z",
    "tender": {
        "tenderPeriod": {"endDate": "2014-12-31T00:00:00Z"},
        "contractPeriod": {"startDate": "2015-12-31T00:00:00Z"},
    },
    "awards": [{"date": "2015-12-30T00:00:00Z", "id": "1"}, {"date": "2017-12-30T00:00:00Z", "id": "2"}],
    "contracts": [
        {"dateSigned": "2015-12-31T00:00:00Z", "awardID": "1"},
        {"dateSigned": "2017-12-31T00:00:00Z", "awardID": "2"},
    ],
}


def test_ok():
    result = calculate(item_ok)
    assert type(result) is dict
    assert result["result"] is True
    assert result["application_count"] == 11
    assert result["pass_count"] == 11
    assert result["meta"] is None


item_failed = {
    "date": "2011-12-31T00:00:00Z",
    "tender": {
        "tenderPeriod": {"endDate": "2021-12-31T00:00:00Z"},
        "contractPeriod": {"startDate": "2020-12-31T00:00:00Z"},
    },
    "awards": [{"date": "2015-12-31T00:00:00Z", "id": "1"}, {"date": "2017-12-31T00:00:00Z", "id": "3"}],
    "contracts": [
        {"dateSigned": "2015-12-30T00:00:00Z", "awardID": "1"},
        {"dateSigned": "2017-12-30T00:00:00Z", "awardID": "2"},
    ],
}


def test_failed():
    result = calculate(item_failed)
    assert type(result) is dict
    assert result["result"] is False
    assert result["application_count"] == 10
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {
                "path_1": "tender.tenderPeriod.endDate",
                "path_2": "tender.contractPeriod.startDate",
                "value_1": "2021-12-31T00:00:00Z",
                "value_2": "2020-12-31T00:00:00Z",
            },
            {
                "path_1": "tender.tenderPeriod.endDate",
                "path_2": "awards[0].date",
                "value_1": "2021-12-31T00:00:00Z",
                "value_2": "2015-12-31T00:00:00Z",
            },
            {
                "path_1": "tender.tenderPeriod.endDate",
                "path_2": "awards[1].date",
                "value_1": "2021-12-31T00:00:00Z",
                "value_2": "2017-12-31T00:00:00Z",
            },
            {
                "path_1": "tender.tenderPeriod.endDate",
                "path_2": "contracts[0].dateSigned",
                "value_1": "2021-12-31T00:00:00Z",
                "value_2": "2015-12-30T00:00:00Z",
            },
            {
                "path_1": "tender.tenderPeriod.endDate",
                "path_2": "contracts[1].dateSigned",
                "value_1": "2021-12-31T00:00:00Z",
                "value_2": "2017-12-30T00:00:00Z",
            },
            {
                "path_1": "awards[0].date",
                "path_2": "date",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2011-12-31T00:00:00Z",
            },
            {
                "path_1": "awards[1].date",
                "path_2": "date",
                "value_1": "2017-12-31T00:00:00Z",
                "value_2": "2011-12-31T00:00:00Z",
            },
            {
                "path_1": "contracts[0].dateSigned",
                "path_2": "date",
                "value_1": "2015-12-30T00:00:00Z",
                "value_2": "2011-12-31T00:00:00Z",
            },
            {
                "path_1": "contracts[1].dateSigned",
                "path_2": "date",
                "value_1": "2017-12-30T00:00:00Z",
                "value_2": "2011-12-31T00:00:00Z",
            },
            {
                "path_1": "awards[0].date",
                "path_2": "contracts[0].dateSigned",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2015-12-30T00:00:00Z",
            },
        ]
    }


item_failed_in_contracts = {
    "contracts": [
        {
            "dateSigned": "2015-12-30T00:00:00Z",
            "implementation": {"transactions": [{"date": "2014-12-30T00:00:00Z"}, {"date": "2014-12-30T00:00:00Z"}]},
        },
        {"dateSigned": "2015-12-30T00:00:00Z", "implementation": {"transactions": [{"date": "2014-12-30T00:00:00Z"}]}},
    ]
}


def test_failed_in_contracts():
    result = calculate(item_failed_in_contracts)
    assert type(result) is dict
    assert result["result"] is False
    assert result["application_count"] == 3
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {
                "path_1": "contracts[0].dateSigned",
                "path_2": "contracts[0].implementation.transactions[0].date",
                "value_1": "2015-12-30T00:00:00Z",
                "value_2": "2014-12-30T00:00:00Z",
            },
            {
                "path_1": "contracts[0].dateSigned",
                "path_2": "contracts[0].implementation.transactions[1].date",
                "value_1": "2015-12-30T00:00:00Z",
                "value_2": "2014-12-30T00:00:00Z",
            },
            {
                "path_1": "contracts[1].dateSigned",
                "path_2": "contracts[1].implementation.transactions[0].date",
                "value_1": "2015-12-30T00:00:00Z",
                "value_2": "2014-12-30T00:00:00Z",
            },
        ]
    }
