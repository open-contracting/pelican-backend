from contracting_process.consistent.number_of_tenderers import calculate

item_ok = {
    "tender": {
        "numberOfTenderers": 2,
        "tenderers": [
            {
                "quantity": 4.0,
            },
            {
                "quantity": 5.0,
            },
        ],
    }
}


item_failed = {
    "tender": {
        "numberOfTenderers": 1,
        "tenderers": [
            {
                "quantity": 4.0,
            },
            {
                "quantity": 5.0,
            },
        ],
    }
}

item_undefined = {
    "tender": {
        "tenderers": [
            {
                "quantity": 4.0,
            },
            {
                "quantity": 5.0,
            },
        ],
    }
}


def test_general():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["value"] is 0
    assert empty_result["meta"] == {"reason": "missing tender key"}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result["result"] is True
    assert result["value"] is 100
    assert result["meta"] is None


def test_failed():
    result = calculate(item_failed)
    assert type(result) == dict
    assert result["result"] is False
    assert result["value"] is 0
    assert result["meta"] == {"numberOfTenderers": 1, "tenderers": [
        {
            "quantity": 4.0,
        },
        {
            "quantity": 5.0,
        },
    ], }


def test_undefined():
    result = calculate(item_undefined)
    assert type(result) == dict
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "incomplete data for comparsion"}
