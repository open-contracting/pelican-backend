from tools.checks import get_empty_result_resource
from tools.getter import get_values

"""
author: Iaroslav Kolodka

"""


version = "1.0"


def calculate(item, path: str) -> dict:
    """ Resource level - OrganizationReference.name.consistent

    Result of this check consists of the application of 'OrganizationReference.name.consistent' rule.

    It fails if
    -------------
        the name of the referenced organization from parties does not equal the organization's name

    It passes if
    -------------
        the name of the referenced organization from parties equals the organization's name

    Parametres
    -------------
    item: dict
        tested JSON
    path: str
        path to the test object

    Returns
    -------------
    result: dict
        result - is result success
        value - None
        application_count - application count
        pass_count - pass_count
        meta -> references -
                    organization_id - organization.id
                    expected_name - expected name
                    referenced_party_path - referenced organization from parties array
                    resource_path - identification of a resource

    """

    result = get_empty_result_resource(version)
    parties = get_values(item, "parties")
    parties_values = [
        elem for elem in parties
        if "id" in elem["value"] and elem["value"]["id"]
    ]
    application_count = 0
    pass_count = 0
    if parties_values:

        parties_id = [
            part["value"]["id"] for part in parties_values
        ]
        values = get_values(item, path)
        values_to_check = [
            value for value in values
            if "id" in value["value"] and value["value"]["id"] and
            parties_id.count(str(value["value"]["id"])) == 1
        ]
        if values_to_check:

            result["meta"] = {"references": []}
            for value in values_to_check:
                referenced_part = None
                for part in parties_values:
                    if str(part["value"]["id"]) == str(value["value"]["id"]):
                        referenced_part = part
                        break
                if not parties_values:
                    continue

                if not "name" in value["value"]:
                    continue
                expected_name = str(value["value"]["name"])

                passed = True
                if not "name" in referenced_part["value"]:
                    passed = False
                else:
                    passed = (
                        expected_name == referenced_part["value"]["name"]
                    )

                application_count += 1
                pass_count = pass_count + 1 if passed else pass_count

                result["meta"]["references"].append(
                    {
                        "organization_id": value["value"]["id"],
                        "expected_name": expected_name,
                        "referenced_party_path": referenced_part["path"],
                        "resource_path": value["path"],

                    }
                )
                result["result"] = application_count == pass_count
        else:
            result["meta"] = {
                "reason": "there are no values with check-specific properties"
            }
    else:
        result["meta"] = {
            "reason": "there are no parties with id set"
        }
    result["application_count"] = application_count
    result["pass_count"] = pass_count
    return result
