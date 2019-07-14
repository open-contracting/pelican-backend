from contracting_process.resource_level.consistent.buyer_roles import calculate


def test_general():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "incomplete data for comparsion"}


item_ok = {
    "buyer": {
        "name": "aaa",
        "id": "aaa"
    },
    "parties": [
        {
            "name": "aaa",
            "id": "aaa",
            "roles": ["buyer", "other_role"]
        },
        {
            "name": "bbb",
            "id": "bbb"
        }
    ]
}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "party": {
            "name": "aaa",
            "id": "aaa",
            "roles": ["buyer", "other_role"]
        }
    }


item_failed_1 = {
    "buyer": {
        "name": "aaa",
        "id": "aaa"
    },
}


item_failed_2 = {
    "buyer": {
        "name": "aaa",
        "id": "aaa"
    },
    "parties": [],
}


item_failed_3 = {
    "buyer": {
        "name": "aaa",
        "id": "aaa"
    },
    "parties": [
        {
            "name": "aaa",
            "id": "aaa",
            "roles": ["other_role"]
        },
        {
            "name": "bbb",
            "id": "bbb"
        }
    ]
}


def test_failed():
    result = calculate(item_failed_1)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "missing parties array"}

    result = calculate(item_failed_2)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "missing parties array"}

    result = calculate(item_failed_3)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "reason": "no organization with buyer role",
        "parties": [
            {
                "name": "aaa",
                "id": "aaa",
                "roles": ["other_role"]
            },
        ]}
