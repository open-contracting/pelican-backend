import functools

from contracting_process.resource_level.consistent import roles

calculate = functools.partial(roles.calculate_path_role, path="buyer", role="buyer")

item_test_undefined1 = {"parties": [{"id": "0"}]}

item_test_undefined2 = {"parties": [{"id": "0"}], "buyer": {}}

item_test_undefined3 = {"parties": [{"id": "0"}, {"id": "0"}], "buyer": {"id": "0"}}


def test_undefined():
    result = calculate({})
    assert result["result"] is None
    assert result["value"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no parties with id set"}

    result = calculate(item_test_undefined1)
    assert result["result"] is None
    assert result["value"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no values with check-specific properties"}

    result = calculate(item_test_undefined2)
    assert result["result"] is None
    assert result["value"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no values with check-specific properties"}

    result = calculate(item_test_undefined3)
    assert result["result"] is None
    assert result["value"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no values with check-specific properties"}


item_test_passed = {"parties": [{"id": "0", "roles": ["buyer"]}], "buyer": {"id": "0"}}


def test_passed():
    result = calculate(item_test_passed)
    assert result["result"] is True
    assert result["value"] is None
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "references": [
            {
                "organization.id": "0",
                "expected_role": "buyer",
                "referenced_party_path": "parties[0]",
                "referenced_party": item_test_passed["parties"][0],
                "resource_path": "buyer",
                "resource": item_test_passed["buyer"],
                "result": True,
            }
        ]
    }


item_test_failed1 = {"parties": [{"id": "0", "roles": []}], "buyer": {"id": "0"}}


def test_failed():
    result = calculate(item_test_failed1)
    assert result["result"] is False
    assert result["value"] is None
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "references": [
            {
                "organization.id": "0",
                "expected_role": "buyer",
                "referenced_party_path": "parties[0]",
                "referenced_party": item_test_failed1["parties"][0],
                "resource_path": "buyer",
                "resource": item_test_failed1["buyer"],
                "result": False,
            }
        ]
    }
