from contracting_process.resource_level.reference.supplier_in_parties import \
    calculate

item_ok = {
    "awards": [
        {
            "suppliers": [
                {
                    "name": "aaa",
                    "id": "aaa"
                },
                {
                    "name": "bbb",
                    "id": "bbb"
                }
            ]
        }
    ],
    "parties": [
        {
            "name": "aaa",
            "id": "aaa"
        },
        {
            "name": "bbb",
            "id": "bbb"
        }
    ]
}


def test_general():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "no suppliers available"}


def test_ok():
    result = calculate(item_ok)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] is 2
    assert result["pass_count"] is 2
    assert result["version"] == 1.0
    assert result["meta"] == {}


item_failed = {
    "awards": [
        {
            "suppliers": [
                {
                    "name": "aaa",
                    "id": "aaa"
                },
                {
                    "name": "bbb",
                    "id": "bbb"
                }
            ]
        }
    ],
    "parties": [
        {
            "name": "bbb",
            "id": "bbb"
        }
    ]
}


def test_failed():
    result = calculate(item_failed)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] is 2
    assert result["pass_count"] is 1
    assert result["version"] == 1.0
    assert result["meta"] == {}
