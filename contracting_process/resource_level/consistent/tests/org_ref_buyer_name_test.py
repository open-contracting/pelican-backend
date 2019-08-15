import functools

from contracting_process.resource_level.consistent.org_ref_name import \
    calculate
from tools.checks import get_empty_result_resource

version = "1.0"

calculate_prepared = functools.partial(
    calculate,
    path="buyer"
)

buyer_item_ok = {
    "parties": [
        {
            "id": "0",
            "name": "aaa",
            "roles": ["buyer"]
        },
        {
            "id": "123",
            "name": "aaa",
            "roles": ["buyer"]
        }
    ],
    "buyer": {
        "id": "0",
        "name": "aaa"
    }
}

buyer_item_failed_wrong_name = {
    "parties": [
        {
            "id": "0",
            "name": "bbb",
            "roles": ["buyer"]
        },
        {
            "id": "123",
            "name": "ccc",
            "roles": ["buyer"]
        }
    ],
    "buyer": {
        "id": "0",
        "name": "aaa"
    }
}

buyer_item_failed_wrong_ids = {
    "parties": [
        {
            "id": "1",
            "name": "bbb",
            "roles": ["buyer"]
        },
        {
            "id": "2",
            "name": "ccc",
            "roles": ["buyer"]
        }
    ],
    "buyer": {
        "id": "0",
        "name": "aaa"
    }
}

buyer_item_failed_no_parties = {
    "parties": [
    ],
    "buyer": {
        "id": "0",
        "name": "aaa"
    }
}

buyer_item_failed_no_buyer1 = {
    "parties": [
        {
            "id": "1",
            "name": "bbb",
            "roles": ["buyer"]
        },
    ],
}
buyer_item_failed_no_buyer2 = {
    "parties": [
    ],
}


def test_fail():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = False
    expected_result["value"] = None
    expected_result["application_count"] = 1
    expected_result["pass_count"] = 0
    expected_result["meta"] = {
        "references": [
            {
                "organization.id": "0",
                "expected_name": "aaa",
                "referenced_party_path": "parties[0]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "buyer",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            }
        ]
    }
    result = calculate_prepared(buyer_item_failed_wrong_name)
    assert result == expected_result


def test_no_action():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = None
    expected_result["value"] = None
    expected_result["application_count"] = None
    expected_result["pass_count"] = None
    expected_result["meta"] = {
        "reason": "there are no values with check-specific properties"
    }
    result = calculate_prepared(buyer_item_failed_wrong_ids)
    assert result == expected_result
    # next
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = None
    expected_result["value"] = None
    expected_result["application_count"] = None
    expected_result["pass_count"] = None
    expected_result["meta"] = {
        "reason": "there are no parties with id set"
    }
    result = calculate_prepared(buyer_item_failed_no_parties)
    assert result == expected_result
    # next
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = None
    expected_result["value"] = None
    expected_result["application_count"] = None
    expected_result["pass_count"] = None
    expected_result["meta"] = {
        "reason": "there are no parties with id set"
    }
    result = calculate_prepared(buyer_item_failed_no_buyer1)
    result = calculate_prepared(buyer_item_failed_no_buyer2)
    assert result == expected_result


def test_ok():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = True
    expected_result["value"] = None
    expected_result["application_count"] = 1
    expected_result["pass_count"] = 1
    expected_result["meta"] = {
        "references": [
            {
                "organization.id": "0",
                "expected_name": "aaa",
                "referenced_party_path": "parties[0]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "buyer",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            }
        ]
    }
    result = calculate_prepared(buyer_item_ok)
    assert result == expected_result
