from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = "1.0"

"""
author: Iaroslav Kolodka

Method is designed to test items from parties on existing refereced items (depending on role)

paramtertes:
    - item: testing JSON
    - path: path to referenced items
    - role: testing role

"""


def calculate(item, path, role):
    result = get_empty_result_resource(version)
    parties = get_values(item, "parties")
    parties_values = [
        party for party in parties
        if "value" in party and "roles" in party["value"] and "id" in party["value"] and party["value"]["roles"]
    ]
    if not parties_values:
        # result["result"] = False
        result["reason"] = "There are no parties with set role and id"
        return result
    values_from_path = get_values(item, path)
    values_from_path = [
        elem for elem in values_from_path if "value" in elem and "id" in elem["value"]
    ]

    is_passed = None
    pass_count = 0
    application_count = 0
    referenced_item_path = None

    for party in parties:
        is_passed = False
        referenced_item_path = None
        for referenced_item in values_from_path:
            if str(referenced_item["value"]["id"]) is str(party["value"]["id"]):
                referenced_item_path = referenced_item["path"]
                is_passed = True
                break
        application_count += 1
        pass_count = pass_count + 1 if is_passed else pass_count
        result["meta"] = {
            "referenced_party_path": referenced_item_path,
            "examined_role": role,
            "recource_path": party["path"]
        }

    result["application_count"] = application_count
    result["pass_count"] = pass_count
    result["result"] = application_count == pass_count
    return result
