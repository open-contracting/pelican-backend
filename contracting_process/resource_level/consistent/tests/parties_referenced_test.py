from contracting_process.resource_level.consistent.parties_role import calculate
from tools.checks import get_empty_result_resource

"""
author: Iaroslav Kolodka

The file contain tests for a 'function contracting_process.resource_level.consistent.parties_role.calculate' .

'test_on_inaction' - an input item has no valid parties -> "There are no parties with set role and id"
'test_with_correct_input' - an input item has two valid parties with corresponding valid objects
'test_with_incorrect_input' - an inputs has no corresponding valid objects

"""

version = "1.1"

testing_roles = {
    "supplier": "awards.suppliers",
    "tenderer": "tender.tenderers",
    "procuringEntity": "tender.procuringEntity",
    "payer": "contracts.implementation.transactions.payer",
    "payee": "contracts.implementation.transactions.payee",
}

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
            "memberOf": [{"id": "adsjk-fhjdkf", "name": "abcd"}],
        },
    ]
}

correct_item_with_payee = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "contracts": [{"implementation": {"transactions": [{"payee": {"id": "010101-a01010"}}]}}],
}


correct_item_with_payer = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["payer"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "contracts": [{"implementation": {"transactions": [{"payer": {"id": "010101-a01015"}}]}}],
}

correct_item_with_tenderer = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["tenderer"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "tender": [{"tenderers": {"id": "010101-a01015"}}],
}


correct_item_with_procuring_entity = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["procuringEntity"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "tender": [{"procuringEntity": {"id": "010101-a01015"}}],
}

correct_item_with_supplier = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["supplier"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "awards": [{"suppliers": {"id": "010101-a01015"}}],
}


incorrect_item_with_payee = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "contracts": [{"implementation": {"transactions": [{"payee": {"id": "00000000000"}}]}}],
}

incorrect_item_with_payer = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["payer"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "contracts": [{"implementation": {"transactions": [{"payer": {"id": "010101-a01010"}}]}}],
}

incorrect_item_with_tenderer = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["tenderer"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "tender": [{"tenderers": {"id": "wrongID"}}],
}

incorrect_item_with_procuring_entity = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["procuringEntity"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "tender": [{"procuringEntity": {"id": "wrongID"}}],
}

incorrect_item_with_supplier = {
    "parties": [
        {
            "id": "010101-a01015",  # empty list of roles
            "name": "Uni",
            "roles": ["supplier"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ],
    "awards": [{"suppliers": {"id": "wrongID"}}],
}


incorrect_item_with_no_payee = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ]
}

incorrect_item_with_no_payer = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payer"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ]
}

incorrect_item_with_no_tenderer = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["tenderer"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ]
}

incorrect_item_with_no_supplier = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["supplier"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ]
}

incorrect_item_with_no_procuring_entity = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["procuringEntity"],
            "memberOf": [{"id": "0rw29R-11341234", "name": "aabbcc"}],
        }
    ]
}


def test_on_inaction():
    expecting_result = get_empty_result_resource(version)
    expecting_result["reason"] = "There are no parties with set role and id"
    for role in testing_roles:
        result = calculate(item_with_no_correct_parties, role, testing_roles[role])
        assert expecting_result == result


def test_with_correct_input():
    expecting_result = get_empty_result_resource(version)
    expecting_result["result"] = True
    # expecting_result["value"] = None  # already None
    expecting_result["application_count"] = 1
    expecting_result["pass_count"] = 1
    expecting_result["meta"] = {"references": []}
    expecting_result["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "payee",
            "resource_identification": "010101-a01010",
            "result": True,
        }
    ]
    result = calculate(correct_item_with_payee, role="payee", path=testing_roles["payee"])
    assert expecting_result == result

    expecting_result["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "payer",
            "resource_identification": "010101-a01015",
            "result": True,
        }
    ]
    result = calculate(correct_item_with_payer, role="payer", path=testing_roles["payer"])
    assert expecting_result == result

    expecting_result["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "payer",
            "resource_identification": "010101-a01015",
            "result": True,
        }
    ]
    result = calculate(correct_item_with_payer, role="payer", path=testing_roles["payer"])
    assert expecting_result == result

    expecting_result["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "tenderer",
            "resource_identification": "010101-a01015",
            "result": True,
        }
    ]
    result = calculate(correct_item_with_tenderer, role="tenderer", path=testing_roles["tenderer"])
    assert expecting_result == result

    expecting_result["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "supplier",
            "resource_identification": "010101-a01015",
            "result": True,
        }
    ]
    result = calculate(correct_item_with_supplier, role="supplier", path=testing_roles["supplier"])
    assert expecting_result == result

    expecting_result["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "procuringEntity",
            "resource_identification": "010101-a01015",
            "result": True,
        }
    ]
    result = calculate(
        correct_item_with_procuring_entity, role="procuringEntity", path=testing_roles["procuringEntity"]
    )
    assert expecting_result == result


def test_with_incorrect_input():
    expecting_result1 = get_empty_result_resource(version)
    expecting_result1["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result1["application_count"] = 1
    expecting_result1["pass_count"] = 0
    expecting_result1["meta"] = {"references": []}
    expecting_result1["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "payee",
            "resource_identification": "010101-a01010",
            "result": False,
        }
    ]
    result1 = calculate(incorrect_item_with_payee, role="payee", path=testing_roles["payee"])
    assert expecting_result1 == result1

    expecting_result1["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "payer",
            "resource_identification": "010101-a01015",
            "result": False,
        }
    ]
    result1 = calculate(incorrect_item_with_payer, role="payer", path=testing_roles["payer"])
    assert expecting_result1 == result1

    expecting_result1["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "tenderer",
            "resource_identification": "010101-a01015",
            "result": False,
        }
    ]
    result1 = calculate(incorrect_item_with_tenderer, role="tenderer", path=testing_roles["tenderer"])
    assert expecting_result1 == result1

    expecting_result1["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "supplier",
            "resource_identification": "010101-a01015",
            "result": False,
        }
    ]
    result1 = calculate(incorrect_item_with_supplier, role="supplier", path=testing_roles["supplier"])
    assert expecting_result1 == result1

    expecting_result1["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "procuringEntity",
            "resource_identification": "010101-a01015",
            "result": False,
        }
    ]
    result1 = calculate(
        incorrect_item_with_procuring_entity, role="procuringEntity", path=testing_roles["procuringEntity"]
    )
    assert expecting_result1 == result1


def test_with_incorrect_input_no_role():
    expecting_result2 = get_empty_result_resource(version)
    expecting_result2["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result2["application_count"] = 1
    expecting_result2["pass_count"] = 0
    expecting_result2["meta"] = {"references": []}
    expecting_result2["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "payee",
            "resource_identification": "010101-a01010",
            "result": False,
        }
    ]
    result2 = calculate(incorrect_item_with_no_payee, role="payee", path=testing_roles["payee"])
    assert expecting_result2 == result2

    expecting_result2["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "payer",
            "resource_identification": "010101-a01010",
            "result": False,
        }
    ]
    result2 = calculate(incorrect_item_with_no_payer, role="payer", path=testing_roles["payer"])
    assert expecting_result2 == result2

    expecting_result2["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "tenderer",
            "resource_identification": "010101-a01010",
            "result": False,
        }
    ]
    result2 = calculate(incorrect_item_with_no_tenderer, role="tenderer", path=testing_roles["tenderer"])
    assert expecting_result2 == result2

    expecting_result2["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "supplier",
            "resource_identification": "010101-a01010",
            "result": False,
        }
    ]
    result2 = calculate(incorrect_item_with_no_supplier, role="supplier", path=testing_roles["supplier"])
    assert expecting_result2 == result2

    expecting_result2["meta"]["references"] = [
        {
            "party_path": "parties[0]",
            "examined_role": "procuringEntity",
            "resource_identification": "010101-a01010",
            "result": False,
        }
    ]
    result2 = calculate(
        incorrect_item_with_no_procuring_entity, role="procuringEntity", path=testing_roles["procuringEntity"]
    )
    assert expecting_result2 == result2
