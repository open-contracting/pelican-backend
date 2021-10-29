import functools

from contracting_process.resource_level.reference.parties import calculate_path

calculate_buyer = functools.partial(calculate_path, path="buyer")

item_test_undefined = {"parties": [{"id": "1"}]}


def test_undefined():
    result = calculate_buyer(item_test_undefined)
    assert result["result"] is None
    assert result["application_count"] == 0
    assert result["pass_count"] == 0
    assert result["meta"] == {"reason": "there are no values with check-specific properties"}


calculate_tender_tenderers = functools.partial(calculate_path, path="tender.tenderers")

item_test_passed1 = {
    "parties": [
        {"id": "0"},
    ],
    "tender": {"tenderers": [{"id": "0"}]},
}
item_test_passed2 = {
    "parties": [
        {"id": "0"},
        {"id": "1"},
    ],
    "tender": {"tenderers": [{"id": "0"}, {"id": "1"}]},
}


def test_passed():
    result = calculate_tender_tenderers(item_test_passed1)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {"failed": []}

    result = calculate_tender_tenderers(item_test_passed2)
    assert result["result"] is True
    assert result["application_count"] == 2
    assert result["pass_count"] == 2
    assert result["meta"] == {"failed": []}


calculate_awards_suppliers = functools.partial(calculate_path, path="awards.suppliers")

item_test_failed1 = {"awards": [{"suppliers": [{}]}]}
item_test_failed2 = {
    "parties": [
        {"id": "1"},
    ],
    "awards": [
        {
            "suppliers": [{"id": "0"}],
        }
    ],
}
item_same_id = {
    "parties": [
        {"id": "0"},
        {"id": "0", "name": ""},
    ],
    "awards": [
        {
            "suppliers": [{"id": "0"}],
        }
    ],
}
item_test_failed4 = {
    "parties": [
        {"id": "0"},
    ],
    "awards": [
        {
            "suppliers": [{"id": "0"}],
        },
        {
            "suppliers": [{"id": "1"}],
        },
    ],
}


def test_failed():
    result = calculate_awards_suppliers(item_test_failed1)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"failed": [{"path": "awards[0].suppliers[0]", "reason": "id missing"}]}

    result = calculate_awards_suppliers(item_test_failed2)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed": [{"path": "awards[0].suppliers[0]", "reason": "party with specified id is not present"}]
    }

    result = calculate_awards_suppliers(item_same_id)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "failed": [{"path": "awards[0].suppliers[0]", "reason": "there are multiple parties with specified id"}]
    }

    result = calculate_awards_suppliers(item_test_failed4)
    assert result["result"] is False
    assert result["application_count"] == 2
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "failed": [{"path": "awards[1].suppliers[0]", "reason": "party with specified id is not present"}]
    }
