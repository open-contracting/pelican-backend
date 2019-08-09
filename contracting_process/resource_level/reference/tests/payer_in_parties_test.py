import functools

from contracting_process.resource_level.reference import parties
calculate = functools.partial(
    parties.calculate_path, path="contracts.implementation.transactions.payer"
)

item_complex = {
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "name": "aaa",
                            "id": "aaa"
                        },
                    },
                    {
                        "payer": {
                            "name": "bbb",
                            "id": "bbb"
                        },
                    }
                ]
            },
        },
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "name": "aaa",
                            "id": "aaa"
                        },
                    },
                    {
                        "payer": {
                            "name": "ccc",
                            "id": "ccc"
                        },
                    }
                ]
            },
        },
    ],
    "parties": [
        {
            "name": "bbb",
            "id": "ddd"
        },
        {
            "name": "aaa",
            "id": "aaa"
        }
    ]
}


def test_complex():
    result = calculate(item_complex)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] is 4
    assert result["pass_count"] is 2
    assert result["version"] == 1.0
    assert result["meta"] == {
        "failed_paths": [
            "contracts[0].implementation.transactions[1].payer",
            "contracts[1].implementation.transactions[1].payer",
        ]
    }
