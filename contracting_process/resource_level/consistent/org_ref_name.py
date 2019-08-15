from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = "1.0"


def calculate(item, path):
    result = get_empty_result_resource(version)
    parties = get_values(item, "parties")
    parties_values = [
        elem for elem in parties
        if "id" in elem["value"] and elem["value"]["id"]
    ]
    if not parties_values:
        result["meta"] = {
            "reason": "there are no parties with id set"
        }
        return result

    parties_id = [
        part["value"]["id"] for part in parties_values
    ]
    values = get_values(item, path)
    values_to_check = [
        value for value in values
        if "id" in value["value"] and value["value"]["id"] and
        parties_id.count(str(value["value"]["id"])) == 1
    ]
    if not values_to_check:
        result["meta"] = {
            "reason": "there are no values with check-specific properties"
        }
        return result
    result["meta"] = {"references": []}
    application_count = 0
    pass_count = 0
    for value in values_to_check:
        referenced_part = ""
        for part in parties_values:
            if str(part["value"]["id"]) == str(value["value"]["id"]):
                referenced_part = part
                break
        if not parties_values:
            continue
        expected_name = str(value["value"]["name"])
        passed = (
            expected_name is referenced_part["value"]["name"]
        )
        application_count += 1
        pass_count = pass_count + 1 if passed else pass_count

        result["meta"]["references"].append(
            {
                "organization.id": value["value"]["id"],
                "expected_name": expected_name,
                "referenced_party_path": referenced_part["path"],
                "resource_path": value["path"],

            }
        )
        result["result"] = application_count == pass_count
        result["application_count"] = application_count
        result["pass_count"] = pass_count
    return result
