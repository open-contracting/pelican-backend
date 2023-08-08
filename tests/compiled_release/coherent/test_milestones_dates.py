from contracting_process.resource_level.coherent.milestones_dates import calculate


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) is dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "no pairs of dates are set"}


item_ok = {
    "date": "2019-12-31T00:00:00Z",
    "planning": {"milestones": [{"dateModified": "2014-12-31T00:00:00Z"}, {"dateMet": "2015-12-31T00:00:00Z"}]},
    "tender": {"milestones": [{"dateModified": "2015-12-31T00:00:00Z"}]},
    "contracts": [
        {
            "milestones": [{"dateModified": "2015-12-31T00:00:00Z", "dateMet": "2017-12-31T00:00:00Z"}],
        },
        {
            "implementation": {
                "milestones": [{"dateModified": "2015-12-30T00:00:00Z"}, {"dateMet": "2017-12-30T00:00:00Z"}]
            }
        },
    ],
}


def test_ok():
    result = calculate(item_ok)
    assert type(result) is dict
    assert result["result"] is True
    assert result["application_count"] == 7
    assert result["pass_count"] == 7
    assert result["meta"] is None


item_failed = {
    "date": "2000-12-31T00:00:00Z",
    "contracts": [
        {
            "milestones": [{"dateModified": "2015-12-31T00:00:00Z", "dateMet": "2017-12-31T00:00:00Z"}],
        },
        {
            "implementation": {
                "milestones": [{"dateModified": "2015-12-30T00:00:00Z"}, {"dateMet": "2017-12-30T00:00:00Z"}]
            }
        },
    ],
}


def test_failed():
    result = calculate(item_failed)
    assert type(result) is dict
    assert result["result"] is False
    assert result["application_count"] == 4
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {
                "path_1": "contracts[0].milestones[0].dateModified",
                "path_2": "date",
                "value_1": "2015-12-31T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
            {
                "path_1": "contracts[0].milestones[0].dateMet",
                "path_2": "date",
                "value_1": "2017-12-31T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
            {
                "path_1": "contracts[1].implementation.milestones[0].dateModified",
                "path_2": "date",
                "value_1": "2015-12-30T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
            {
                "path_1": "contracts[1].implementation.milestones[1].dateMet",
                "path_2": "date",
                "value_1": "2017-12-30T00:00:00Z",
                "value_2": "2000-12-31T00:00:00Z",
            },
        ]
    }
