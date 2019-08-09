import functools

from contracting_process.resource_level.reference import parties
calculate = functools.partial(
    parties.calculate_path, path="contracts.implementation.transactions.payee"
)

item_complex = {
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payee": {
                            "name": "aaa",
                            "id": "aaa"
                        },
                    },
                    {
                        "payee": {
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
                        "payee": {
                            "name": "aaa",
                            "id": "aaa"
                        },
                    },
                    {
                        "payee": {
                            "name": "ccc",
                            "id": "aaa"
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
    assert result["pass_count"] is 3
    assert result["version"] == 1.0
    assert result["meta"] == {
        "failed_paths": [
            "contracts[0].implementation.transactions[1].payee",
        ]
    }
