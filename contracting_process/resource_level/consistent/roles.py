from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate_path_role(item, path, role):
    result = get_empty_result_resource(version)

    values = get_values(item, "parties")
    parties_values = [v for v in values if "id" in v["value"] and v["value"]["id"] is not None]

    if not parties_values:
        result["meta"] = {"reason": "there are no parties with id set"}
        return result

    parties_id = [p["value"]["id"] for p in parties_values]

    values = get_values(item, path)
    check_values = [
        v
        for v in values
        if "id" in v["value"] and v["value"]["id"] is not None and parties_id.count(str(v["value"]["id"])) == 1
    ]

    if not check_values:
        result["meta"] = {"reason": "insufficient data for check"}
        return result

    result["meta"] = {"references": []}
    application_count = 0
    pass_count = 0
    for value in check_values:
        referenced_party = [p for p in parties_values if p["value"]["id"] == str(value["value"]["id"])][0]
        passed = (
            "roles" in referenced_party["value"]
            and referenced_party["value"]["roles"] is not None
            and role in referenced_party["value"]["roles"]
        )

        application_count += 1
        if passed:
            pass_count += 1

        result["meta"]["references"].append(
            {
                "organization.id": str(value["value"]["id"]),
                "expected_role": role,
                "referenced_party_path": referenced_party["path"],
                "referenced_party": referenced_party["value"],
                "resource_path": value["path"],
                "resource": value["value"],
                "result": passed,
            }
        )

    return complete_result_resource(result, application_count, pass_count)
