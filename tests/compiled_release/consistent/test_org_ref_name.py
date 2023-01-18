import functools

from contracting_process.resource_level.consistent.org_ref_name import calculate

calculate_buyer = functools.partial(calculate, path="buyer")

item_test_undefined1 = {"parties": [], "buyer": {"id": "0", "name": "aaa"}}
item_test_undefined2 = {
    "parties": [
        {
            "id": "1",
            "name": "bbb",
        },
        {
            "id": "2",
            "name": "ccc",
        },
    ],
    "buyer": {"id": "0", "name": "aaa"},
}
item_test_undefined3 = {
    "parties": [
        {
            "id": "0",
            "name": "aaa",
        },
        {
            "id": "0",
            "name": "bbb",
        },
    ],
    "buyer": {"id": "0", "name": "aaa"},
}


def test_undefined():
    result = calculate_buyer(item_test_undefined1)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no parties with unique id and name set"}

    result = calculate_buyer(item_test_undefined2)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "insufficient data for check"}

    result = calculate_buyer(item_test_undefined3)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no parties with unique id and name set"}


calculate_tender_tenderers = functools.partial(calculate, path="tender.tenderers")

item_test_passed1 = {
    "parties": [
        {
            "id": "0",
            "name": "aaa",
        },
    ],
    "tender": {"tenderers": [{"id": "0", "name": "aaa"}]},
}
item_test_passed2 = {
    "parties": [
        {
            "id": "0",
            "name": "aaa",
        },
        {
            "id": "1",
            "name": "bbb",
        },
    ],
    "tender": {
        "tenderers": [
            {"id": "0", "name": "aaa"},
            {"id": "0", "name": "aaa", "identifier": {"id": "1"}},
            {"id": "1", "name": "bbb"},
        ]
    },
}


def test_passed():
    result = calculate_tender_tenderers(item_test_passed1)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "references": [
            {
                "party": {"id": "0", "name": "aaa", "path": "parties[0]"},
                "tender.tenderers": {"id": "0", "name": "aaa", "path": "tender.tenderers[0]"},
                "result": True,
            }
        ]
    }

    result = calculate_tender_tenderers(item_test_passed2)
    assert result["result"] is True
    assert result["application_count"] == 3
    assert result["pass_count"] == 3
    assert result["meta"] == {
        "references": [
            {
                "party": {"id": "0", "name": "aaa", "path": "parties[0]"},
                "tender.tenderers": {"id": "0", "name": "aaa", "path": "tender.tenderers[0]"},
                "result": True,
            },
            {
                "party": {"id": "0", "name": "aaa", "path": "parties[0]"},
                "tender.tenderers": {"id": "0", "name": "aaa", "path": "tender.tenderers[1]"},
                "result": True,
            },
            {
                "party": {"id": "1", "name": "bbb", "path": "parties[1]"},
                "tender.tenderers": {"id": "1", "name": "bbb", "path": "tender.tenderers[2]"},
                "result": True,
            },
        ]
    }


calculate_awards_suppliers = functools.partial(calculate, path="awards.suppliers")

item_test_failed1 = {
    "parties": [
        {
            "id": "0",
            "name": "aaa",
        },
    ],
    "awards": [{"suppliers": [{"id": "0", "name": "bbb"}]}],
}
item_test_failed2 = {
    "parties": [
        {
            "id": "0",
            "name": "aaa",
        },
    ],
    "awards": [
        {
            "suppliers": [{"id": "0", "name": "bbb"}],
        },
        {
            "suppliers": [
                {
                    "id": "0",
                    "name": "aaa",
                },
            ]
        },
    ],
}


def test_failed():
    result = calculate_awards_suppliers(item_test_failed1)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "references": [
            {
                "party": {"id": "0", "name": "aaa", "path": "parties[0]"},
                "awards.suppliers": {"id": "0", "name": "bbb", "path": "awards[0].suppliers[0]"},
                "result": False,
            }
        ]
    }

    result = calculate_awards_suppliers(item_test_failed2)
    assert result["result"] is False
    assert result["application_count"] == 2
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "references": [
            {
                "party": {"id": "0", "name": "aaa", "path": "parties[0]"},
                "awards.suppliers": {"id": "0", "name": "bbb", "path": "awards[0].suppliers[0]"},
                "result": False,
            },
            {
                "party": {"id": "0", "name": "aaa", "path": "parties[0]"},
                "awards.suppliers": {"id": "0", "name": "aaa", "path": "awards[1].suppliers[0]"},
                "result": True,
            },
        ]
    }
