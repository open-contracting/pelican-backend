from contracting_process.resource_level.consistent.number_of_tenderers import calculate

item_ok = {
    "tender": {
        "numberOfTenderers": 2,
        "tenderers": [
            {
                "name": "Acme Inc.",
            },
            {
                "name": "Mom and Pop",
            },
        ],
    }
}


item_failed = {
    "tender": {
        "numberOfTenderers": 1,
        "tenderers": [
            {
                "name": "Acme Inc.",
            },
            {
                "name": "Mom and Pop",
            },
        ],
    }
}

item_undefined_number_of_tenderers = {
    "tender": {
        "tenderers": [
            {
                "name": "Acme Inc.",
            },
            {
                "name": "Mom and Pop",
            },
        ],
    }
}

item_undefined_tenderers = {
    "tender": {
        "numberOfTenderers": 1,
    }
}


def test_general():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "numberOfTenderers is non-numeric"}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] is None


def test_failed():
    result = calculate(item_failed)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "numberOfTenderers": 1,
        "tenderers": [
            {
                "name": "Acme Inc.",
            },
            {
                "name": "Mom and Pop",
            },
        ],
    }


def test_undefined_number_of_tenderers():
    result = calculate(item_undefined_number_of_tenderers)
    assert type(result) == dict
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "numberOfTenderers is non-numeric"}


def test_undefined_tenderers():
    result = calculate(item_undefined_tenderers)
    assert type(result) == dict
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "tenderers is not an array"}
