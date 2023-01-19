from contracting_process.resource_level.consistent.parties_role import calculate
from tools.checks import get_empty_result_resource

version = 1.0

item_with_no_correct_parties = {
    "parties": [
        {
            "id": "adsjk-fhjdkf",  # no roles
            "name": "abcd",
            "address": {"streetAddress": "dcba "},
            "identifier": {"scheme": "12-12-12"},
            "contactPoint": {},
        },
        {
            "id": "0rw29R-dsfad",  # empty list of roles
            "name": "Unidad Central",
            "roles": [],
        },
    ]
}

correct_item_with_payee = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
        }
    ],
    "contracts": [{"implementation": {"transactions": [{"payee": {"id": "010101-a01010"}}]}}],
}
incorrect_item_with_payee = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
        }
    ],
    "contracts": [{"implementation": {"transactions": [{"payee": {"id": "00000000000"}}]}}],
}

incorrect_item_with_no_payee = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
        }
    ]
}


def test_on_inaction():
    expecting_result = get_empty_result_resource(version)
    expecting_result["meta"] = {"reason": "There are no parties with set role and id"}
    result = calculate(item_with_no_correct_parties)
    assert expecting_result == result


def test_with_correct_input():
    expecting_result = get_empty_result_resource(version)
    expecting_result["result"] = True
    # expecting_result["value"] = None  # already None
    expecting_result["application_count"] = 1
    expecting_result["pass_count"] = 1
    expecting_result["meta"] = {"references": []}
    expecting_result["meta"]["references"] = [
        {"party_path": "parties[0]", "examined_role": "payee", "resource_identification": "010101-a01010"}
    ]
    result = calculate(correct_item_with_payee)
    assert expecting_result == result


def test_with_incorrect_input():
    expecting_result1 = get_empty_result_resource(version)
    expecting_result1["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result1["application_count"] = 1
    expecting_result1["pass_count"] = 0
    expecting_result1["meta"] = {"references": []}
    expecting_result1["meta"]["references"] = [
        {"party_path": "parties[0]", "examined_role": "payee", "resource_identification": "010101-a01010"}
    ]
    result1 = calculate(incorrect_item_with_payee)
    assert expecting_result1 == result1
    expecting_result2 = get_empty_result_resource(version)
    expecting_result2["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result2["application_count"] = 1
    expecting_result2["pass_count"] = 0
    expecting_result2["meta"] = {"references": []}
    expecting_result2["meta"]["references"] = [
        {"party_path": "parties[0]", "examined_role": "payee", "resource_identification": "010101-a01010"}
    ]
    result2 = calculate(incorrect_item_with_no_payee)
    assert expecting_result2 == result2
