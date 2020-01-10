from contracting_process.resource_level.coherent.tender_status import calculate

item_undefined_1 = {
    "tender": {
    }
}


item_undefined_2 = {
    "tender": {
        "status": "some_status"
    }
}


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "incomplete data for check"}

    empty_result = calculate(item_undefined_1)
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "incomplete data for check"}

    empty_result = calculate(item_undefined_2)
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "non-evaluated tender status"}


item_ok_1 = {
    "tender": {
        "status": "planning",
    }
}

item_ok_2 = {
    "tender": {
        "status": "planning",
    },
    "awards": []
}

item_ok_3 = {
    "tender": {
        "status": "planning",
    },
    "awards": [],
    "contracts": []
}


def test_ok():
    result = calculate(item_ok_1)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] is None

    result = calculate(item_ok_2)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] is None

    result = calculate(item_ok_3)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] is None


item_failed_1 = {
    "tender": {
        "status": "planning",
    },
    "awards": [{"something": 1}]
}

item_failed_2 = {
    "tender": {
        "status": "planning",
    },
    "awards": [],
    "contracts": [{"something": 1}]
}


def test_failed():
    result = calculate(item_failed_1)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"contracts_count": 0, "awards_count": 1}

    result = calculate(item_failed_2)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"contracts_count": 1, "awards_count": 0}
