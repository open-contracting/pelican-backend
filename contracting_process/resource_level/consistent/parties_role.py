from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0

"""
author: Iaroslav Kolodka

"""

testing_roles = {
    "supplier": "awards.suppliers",
    "tenderer": "tender.tenderers",
    "procuringEntity": "tender.procuringEntity",
    "payer": "contracts.implementation.transactions.payer",
    "payee": "contracts.implementation.transactions.payee",
}


def calculate(item) -> dict:
    result = get_empty_result_resource(version)
    parties = get_values(item, "parties")
    parties_roles = []
    for party in parties:
        if "value" in party and party["value"]:
            party_value = party["value"]
            if "roles" in party_value and party_value["roles"] and "id" in party_value and party_value["id"]:
                for role in party_value["roles"]:
                    if role in testing_roles.keys():
                        party_item = {"role": role, "id": party_value["id"], "path": party["path"]}
                        parties_roles.append(party_item)

    if not parties_roles:
        result["meta"] = {"reason": "There are no parties with set role and id"}
        return result

    items_from_paths = []
    for role_name, role_path in testing_roles.items():
        found_items = []
        found_items += get_values(item, role_path)
        for elem in found_items:
            if "value" in elem and "id" in elem["value"]:
                elem_box = {"id": elem["value"]["id"], "role": role_name}
                items_from_paths.append(elem_box)

    passed = None
    pass_count = 0
    application_count = 0

    for party in parties_roles:
        if not result["meta"] or "references" not in result["meta"]:
            result["meta"] = {"references": []}
        passed = False
        role = None
        for referenced_item in items_from_paths:
            if str(referenced_item["id"]) == str(party["id"]) and referenced_item["role"] == party["role"]:
                passed = True
                break
        application_count += 1
        if passed:
            pass_count += 1

        result["meta"]["references"].append(
            {
                # identification of a resource
                "party_path": party["path"],
                # role that was examined
                "examined_role": party["role"],
                # identification of a resource
                "resource_identification": party["id"],
            }
        )

    result["application_count"] = application_count
    result["pass_count"] = pass_count
    result["result"] = application_count == pass_count
    return result
