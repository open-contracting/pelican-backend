import functools

from contracting_process.resource_level.consistent.parties_role import \
    calculate
from tools.checks import get_empty_result_resource

version = "1.0"

calculate_prepared = functools.partial(
    calculate,
    path="tender.tenderers",
    role="tenderer"
)


item_with_no_correct_parties = {
   "parties": [
        {
            "id": "adsjk-fhjdkf",  # no roles
            "name": "abcd",
            "address": {
                "streetAddress": "dcba "
            },
            "identifier": {"scheme": "12-12-12"},
            "contactPoint": {}
        },
        {
            "id": "0rw29R-dsfad",  # empty list of roles
            "name": "Unidad Central",
            "roles": [],
            "memberOf": [
                {"id": "adsjk-fhjdkf", "name": "abcd"}
            ],
        }
    ]
}


correct_item_with_tenderer = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
            "memberOf": [
                {"id": "0rw29R-11341234", "name": "aabbcc"}
            ],
        }
    ],
    "tender": {
        "tenderers": [
            {
                "id": "010101-a01010"
            }
        ]
    }
}
incorrect_item_with_tenderer = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
            "memberOf": [
                {"id": "0rw29R-11341234", "name": "aabbcc"}
            ],
        }
    ],
    "tender": {
        "tenderers": [
            {
                "id": "000000000000"
            }
        ]
    }
}

incorrect_item_with_no_tenderer = {
    "parties": [
        {
            "id": "010101-a01010",  # empty list of roles
            "name": "Uni",
            "roles": ["payee"],
            "memberOf": [
                {"id": "0rw29R-11341234", "name": "aabbcc"}
            ],
        }
    ]
}


def test_on_inaction():
    expecting_result = get_empty_result_resource(version)
    expecting_result["reason"] = "There are no parties with set role and id"
    result = calculate_prepared(item_with_no_correct_parties)
    assert expecting_result == result


def test_correct_tender_tenderer():
    expecting_result = get_empty_result_resource(version)
    expecting_result["result"] = True
    # expecting_result["value"] = None  # already None
    expecting_result["application_count"] = 1
    expecting_result["pass_count"] = 1
    expecting_result["meta"] = {
        "referenced_party_path": "tender.tenderers[0]",
        "examined_role": "tenderer",
        "recource_path": "parties[0]"
    }
    result = calculate_prepared(correct_item_with_tenderer)
    assert expecting_result == result


def test_incorrect_tender_tenderer():
    expecting_result1 = get_empty_result_resource(version)
    expecting_result1["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result1["application_count"] = 1
    expecting_result1["pass_count"] = 0
    expecting_result1["meta"] = {
        "referenced_party_path": None,
        "examined_role": "tenderer",
        "recource_path": "parties[0]"
    }
    result1 = calculate_prepared(incorrect_item_with_tenderer)
    assert expecting_result1 == result1
    expecting_result2 = get_empty_result_resource(version)
    expecting_result2["result"] = False
    # expecting_result["value"] = None  # already None
    expecting_result2["application_count"] = 1
    expecting_result2["pass_count"] = 0
    expecting_result2["meta"] = {
        "referenced_party_path": None,
        "examined_role": "tenderer",
        "recource_path": "parties[0]"
    }
    result2 = calculate_prepared(incorrect_item_with_no_tenderer)
    assert expecting_result2 == result2
