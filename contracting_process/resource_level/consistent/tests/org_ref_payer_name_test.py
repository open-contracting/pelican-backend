import functools

from contracting_process.resource_level.consistent.org_ref_name import \
    calculate
from tools.checks import get_empty_result_resource

version = "1.0"

calculate_prepared = functools.partial(
    calculate,
    path="contracts.implementation.transactions.payer"
)

payer_item_ok = {
    "parties": [
        {
            "id": "000",
            "name": "aaa",
        },
        {
            "id": "111",
            "name": "bbb",
        }
    ],
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "id": "000",
                            "name": "aaa",
                        }
                    }
                ]
            }
        },
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "id": "111",
                            "name": "bbb",
                        }
                    }
                ]
            }
        }
    ]

}
payer_item_fail_partially = {
    "parties": [
        {
            "id": "000",
            "name": "aaa",
        },
        {
            "id": "111",
            "name": "bbb",
        }
    ],
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "id": "000",
                            "name": "aaa",
                        }
                    }
                ]
            }
        },
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "id": "111",
                            "name": "bcd",
                        }
                    }
                ]
            }
        }
    ]

}


def test_fail():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = False
    expected_result["value"] = None
    expected_result["application_count"] = 2
    expected_result["pass_count"] = 1
    expected_result["meta"] = {
        "references": [
            {
                "organization.id": "000",
                "expected_name": "aaa",
                "referenced_party_path": "parties[0]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "contracts[0].implementation.transactions[0].payer",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            },
            {
                "organization.id": "111",
                "expected_name": "bcd",
                "referenced_party_path": "parties[1]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "contracts[1].implementation.transactions[0].payer",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            }
        ]
    }
    result = calculate_prepared(payer_item_fail_partially)
    assert result == expected_result


def test_ok():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = True
    expected_result["value"] = None
    expected_result["application_count"] = 2
    expected_result["pass_count"] = 2
    expected_result["meta"] = {
        "references": [
            {
                "organization.id": "000",
                "expected_name": "aaa",
                "referenced_party_path": "parties[0]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "contracts[0].implementation.transactions[0].payer",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            },
            {
                "organization.id": "111",
                "expected_name": "bbb",
                "referenced_party_path": "parties[1]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "contracts[1].implementation.transactions[0].payer",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            }
        ]
    }
    result = calculate_prepared(payer_item_ok)
    assert result == expected_result
