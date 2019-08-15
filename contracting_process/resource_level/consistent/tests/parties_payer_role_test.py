
import functools

from contracting_process.resource_level.consistent.parties_role import \
    calculate
from tools.checks import get_empty_result_resource

version = "1.0"

calculate_prepared = functools.partial(
    calculate,
    path="contracts.implementation.transactions.payer",
    role="payer"
)

item_with_no_correct_parties = {
    "parties": [
        {
            "id": "7rBOL0",  # no roles
            "name": "Secretaria de Desarrollo Economico",
            "address": {
                "streetAddress": "Edificio San José,3 piso Boulevard KUWAIT "
            },
            "identifier": {"scheme": "HN-ONCAE-CE"},
            "contactPoint": {}
        },
        {
            "id": "0rw29R-7rBOL0",  # empty list of roles
            "name": "Unidad Central",
            "roles": [],
            "memberOf": [
                {"id": "7rBOL0", "name": "Secretaria de Desarrollo Economico"}
            ],
        }
    ]
}

correct_item_with_payer = {
    "parties": [
        {
            "id": "0rw29R-7rBOL0",  # empty list of roles
            "name": "Unidad Central",
            "roles": ["payer"],
            "memberOf": [
                {"id": "7rBOL0", "name": "Secretaria de Desarrollo Economico"}
            ],
        }
    ],
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "id": "0rw29R-7rBOL0"
                        }
                    }
                ]
            }
        }
    ]
}
incorrect_item_with_payer = {
    "parties": [
        {
            "id": "0rw29R-7rBOL0",  # empty list of roles
            "name": "Unidad Central",
            "roles": ["payer"],
            "memberOf": [
                {"id": "7rBOL0", "name": "Secretaria de Desarrollo Economico"}
            ],
        }
    ],
    "contracts": [
        {
            "implementation": {
                "transactions": [
                    {
                        "payer": {
                            "id": "00000000000"
                        }
                    }
                ]
            }
        }
    ]
}

incorrect_item_with_no_payer = {
    "parties": [
        {
            "id": "0rw29R-7rBOL0",  # empty list of roles
            "name": "Unidad Central",
            "roles": ["payer"],
            "memberOf": [
                {"id": "7rBOL0", "name": "Secretaria de Desarrollo Economico"}
            ],
        }
    ]
}


def test_on_inaction():
    expecting_result = get_empty_result_resource(version)
    expecting_result["reason"] = "There are no parties with set role and id"
    result = calculate_prepared(item_with_no_correct_parties)
    assert expecting_result == result


def test_correct_tender_payer():
    expecting_result = get_empty_result_resource(version)
    expecting_result["result"] = True
    # expecting_result["value"] = None  # already None
    expecting_result["application_count"] = 1
    expecting_result["pass_count"] = 1
    expecting_result["meta"] = {
        "referenced_party_path": "contracts[0].implementation.transactions[0].payer",
        "examined_role": "payer",
        "recource_path": "parties[0]"
    }
    result = calculate_prepared(correct_item_with_payer)
    assert expecting_result == result


def test_incorrect_tender_payer():
    expecting_result1 = get_empty_result_resource(version)
    expecting_result1["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result1["application_count"] = 1
    expecting_result1["pass_count"] = 0
    expecting_result1["meta"] = {
        "referenced_party_path": None,
        "examined_role": "payer",
        "recource_path": "parties[0]"
    }
    result1 = calculate_prepared(incorrect_item_with_payer)
    assert expecting_result1 == result1
    expecting_result2 = get_empty_result_resource(version)
    expecting_result2["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result2["application_count"] = 1
    expecting_result2["pass_count"] = 0
    expecting_result2["meta"] = {
        "referenced_party_path": None,
        "examined_role": "payer",
        "recource_path": "parties[0]"
    }
    result2 = calculate_prepared(incorrect_item_with_no_payer)
    assert expecting_result2 == result2
