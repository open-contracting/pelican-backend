import functools

from contracting_process.resource_level.reference import parties
calculate = functools.partial(
    parties.calculate_path, path="tender.tenderers"
)

item_complex = {
    "tender": [
        {
            "tenderers": [
                {
                    "name": "aaa",
                    "id": "aaa"
                },
                {
                    "name": "bbb",
                    "id": "bbb"
                }
            ]
        },
        {
            "tenderers": [
                {
                    "name": "aaa",
                    "id": "aaa"
                },
                {
                    "name": "ccc",
                    "id": "ccc"
                }
            ]
        }
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
            "tender[0].tenderers[1]",
            "tender[1].tenderers[1]",
        ]
    }
