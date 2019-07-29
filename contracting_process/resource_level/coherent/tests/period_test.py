from contracting_process.resource_level.coherent.period import calculate


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "incomplete data for check"}


item_test_multiple_contracts = {
    "contracts":
        [
            {
                "period": {
                    "endDate": "2015-12-31T00:00:00-06:00",
                    "startDate": "2015-10-01T00:00:00-06:00"
                },
            },
            {
                "period": {
                    "endDate": "2015-12-31T00:00:00-06:00",
                    "startDate": "2015-10-01T00:00:00-06:00"
                },
            },
            {
                "period": {
                    "endDate": "2015-12-31T00:00:00-06:00",
                    "startDate": "2015-10-01T00:00:00-06:00"
                },
            }
        ]
}


def test_multiple_contracts():
    result = calculate(item_test_multiple_contracts)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 3
    assert result["pass_count"] == 3
    assert result["meta"] == {"failed_paths": [{"path": "contracts.period[0]", "result": True},
                                               {"path": "contracts.period[1]", "result": True},
                                               {"path": "contracts.period[2]", "result": True}]}


item_test_missing_dates = {
    "tender": {

    },
    "awards": [
        {

        },
        {
            "contractPeriod": {
                "endDate": "2015-12-31T00:00:00-06:00"
            }
        }
    ],
    "contracts": [
        {
            "period": {
                "startDate": "2015-12-31T00:00:00-06:00"
            }
        }
    ]
}


def test_missing_dates():
    result = calculate(item_test_missing_dates)
    assert type(result) == dict
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "incomplete data for check"}


item_test_ill_formatted_dates1 = {
    "tender": {
        "enquiryPeriod": {
            "startDate": "2014-10-21",
            "endDate": "2014-10-21"
        }
    }
}

item_test_ill_formatted_dates2 = {
    "tender": {
        "enquiryPeriod": {
            "startDate": "2014-11-18T18:00:00",
            "endDate": "2015-12-31T00:00:00-06:00"
        }
    }
}


def test_ill_formatted_dates():
    result = calculate(item_test_ill_formatted_dates1)
    assert type(result) == dict
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "incomplete data for check"}

    result = calculate(item_test_ill_formatted_dates2)
    assert type(result) == dict
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "incomplete data for check"}


item_test_one_fail = {
    "tender": {
        "awardPeriod": {
            "startDate": "2015-12-31T00:00:00-06:00",
            "endDate": "2015-12-30T00:00:00-06:00"
        }
    }
}


def test_one_fail():
    result = calculate(item_test_one_fail)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"failed_paths": [{"path": "tender.awardPeriod[0]", "result": False}]}


item_test_mixed_time_zones = {
    "tender": {
        "tenderPeriod": {
            "startDate": "2015-12-30T09:00:00-06:00",
            "endDate": "2015-12-30T08:00:00-07:00"
        }
    }
}


def test_mixed_time_zones():
    result = calculate(item_test_mixed_time_zones)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {"failed_paths": [{"path": "tender.tenderPeriod[0]", "result": True}]}


item_test_multiple_fails_and_passes = {
    "awards": [
        {
            "contractPeriod": {
                "startDate": "2014-12-31T00:00:00Z",
                "endDate": "2015-12-31T00:00:00Z"
            }
        },
        {
            "contractPeriod": {
                "startDate": "2014-12-31T00:00:00Z",
                "endDate": "2015-12-31T00:00:00Z"
            }
        },
        {
            "contractPeriod": {
                "startDate": "2016-12-31T00:00:00Z",
                "endDate": "2015-12-31T00:00:00Z"
            }
        },
        {
            "contractPeriod": {
                "startDate": "2014-12-31T00:00:00Z"
            }
        }
    ]
}


def test_multiple_fails_and_passes():
    result = calculate(item_test_multiple_fails_and_passes)
    print(result)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 3
    assert result["pass_count"] == 2
    assert result["meta"] == {"failed_paths": [{"path": "awards.contractPeriod[0]", "result": True},
                                               {"path": "awards.contractPeriod[1]", "result": True},
                                               {"path": "awards.contractPeriod[2]", "result": False}]}
