import functools

from contracting_process.resource_level.consistent import roles

calculate = functools.partial(
    roles.calculate_path_role, path="contracts.implementation.transactions.payer", role="payer"
)

item_unset = {"parties": [{"id": "0"}]}
item_empty = {"parties": [{"id": "0"}], "contracts": [{"implementation": {"transactions": [{"payer": {}}]}}]}
item_same_id = {
    "parties": [{"id": "0"}, {"id": "0", "name": ""}],
    "contracts": [{"implementation": {"transactions": [{"payer": {"id": "0"}}]}}],
}


def test_undefined():
    result = calculate({})
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "no party has an id"}

    result = calculate(item_unset)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "no reference has an id and matches exactly one party"}

    result = calculate(item_empty)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "no reference has an id and matches exactly one party"}

    result = calculate(item_same_id)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "no reference has an id and matches exactly one party"}


item_test_passed = {
    "parties": [{"id": "0", "roles": ["payer"]}],
    "contracts": [{"implementation": {"transactions": [{"payer": {"id": "0"}}]}}],
}


def test_passed():
    result = calculate(item_test_passed)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] is None


item_test_failed1 = {
    "parties": [{"id": "0", "roles": []}],
    "contracts": [{"implementation": {"transactions": [{"payer": {"id": "0"}}]}}],
}

item_test_failed2 = {
    "parties": [{"id": "0", "roles": ["payer"]}, {"id": "1"}, {"id": "2", "roles": ["unknown"]}],
    "contracts": [
        {"implementation": {"transactions": [{"payer": {"id": "0"}}]}},
        {"implementation": {"transactions": [{"payer": {"id": "1"}}, {"payer": {"id": "2"}}]}},
    ],
}


def test_failed():
    result = calculate(item_test_failed1)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed_paths": [
            {
                "party": {"id": "0", "path": "parties[0]", "roles": []},
                "reference": {"id": "0", "path": "contracts[0].implementation.transactions[0].payer", "role": "payer"},
            }
        ],
    }

    result = calculate(item_test_failed2)
    assert result["result"] is False
    assert result["application_count"] == 3
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "failed_paths": [
            {
                "party": {"id": "1", "path": "parties[1]", "roles": []},
                "reference": {"id": "1", "path": "contracts[1].implementation.transactions[0].payer", "role": "payer"},
            },
            {
                "party": {"id": "2", "path": "parties[2]", "roles": ["unknown"]},
                "reference": {"id": "2", "path": "contracts[1].implementation.transactions[1].payer", "role": "payer"},
            },
        ],
    }
