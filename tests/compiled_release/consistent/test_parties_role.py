from contracting_process.resource_level.consistent.parties_role import calculate

item_test_undefined = {
    "parties": [
        {"id": "1"},
        {"id": "2", "roles": []},
        {"id": "3", "roles": ["buyer"]},
        {"roles": ["tenderer"]},
    ]
}


def test_undefined():
    result = calculate(item_test_undefined)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "no party has an id and an applicable role"}


item_test_passed = {
    "parties": [
        {"id": "1", "roles": ["procuringEntity"]},
        {"id": "2", "roles": ["tenderer"]},
        {"id": "3", "roles": ["supplier"]},
        {"id": "4", "roles": ["payer"]},
        {"id": 5, "roles": ["payee"]},
    ],
    "tender": {
        "procuringEntity": {"id": "1"},
        "tenderers": [{"id": "2"}],
    },
    "awards": [
        {
            "suppliers": [{"id": "3"}],
        }
    ],
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {"id": 4},
                        "payee": {"id": "5"},
                    }
                ]
            }
        }
    ],
}


def test_passed():
    result = calculate(item_test_passed)
    assert result["result"] is True
    assert result["application_count"] == 5
    assert result["pass_count"] == 5
    assert result["meta"] is None


item_test_failed1 = {
    "parties": [
        {"id": "1", "roles": ["procuringEntity"]},
        {"id": "2", "roles": ["tenderer"]},
        {"id": "3", "roles": ["supplier"]},
        {"id": "4", "roles": ["payer"]},
        {"id": 5, "roles": ["payee"]},
    ],
    "tender": {
        "procuringEntity": {"id": "A"},
        "tenderers": [{"id": "B"}],
    },
    "awards": [
        {
            "suppliers": [{"id": "C"}],
        }
    ],
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {"id": "D"},
                        "payee": {"id": "E"},
                    }
                ]
            }
        }
    ],
}

item_test_failed2 = {
    "parties": [
        {"id": "1", "roles": ["procuringEntity"]},
        {"id": "2", "roles": ["tenderer"]},
        {"id": "3", "roles": ["supplier"]},
        {"id": "4", "roles": ["payer"]},
        {"id": 5, "roles": ["payee"]},
    ]
}


def test_failed():
    result = calculate(item_test_failed1)
    assert result["result"] is False
    assert result["application_count"] == 5
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {"path": "parties[0]", "role": "procuringEntity", "id": "1"},
            {"path": "parties[1]", "role": "tenderer", "id": "2"},
            {"path": "parties[2]", "role": "supplier", "id": "3"},
            {"path": "parties[3]", "role": "payer", "id": "4"},
            {"path": "parties[4]", "role": "payee", "id": "5"},
        ]
    }

    result = calculate(item_test_failed2)
    assert result["result"] is False
    assert result["application_count"] == 5
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {"path": "parties[0]", "role": "procuringEntity", "id": "1"},
            {"path": "parties[1]", "role": "tenderer", "id": "2"},
            {"path": "parties[2]", "role": "supplier", "id": "3"},
            {"path": "parties[3]", "role": "payer", "id": "4"},
            {"path": "parties[4]", "role": "payee", "id": "5"},
        ]
    }
