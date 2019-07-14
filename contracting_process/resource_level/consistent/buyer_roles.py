from tools.checks import get_empty_result_resource

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    # completely missing tender value
    if "buyer" not in item or "id" not in item["buyer"]:
        result["result"] = None
        result["meta"] = {"reason": "incomplete data for comparsion"}
        return result

    buyer_id = item["buyer"]["id"]

    if "parties" not in item or not item["parties"]:
        result["result"] = False
        result["application_count"] = 1
        result["pass_count"] = 0
        result["meta"] = {
            "reason": "missing parties array"
        }

        return result

    for party in item["parties"]:
        if "id" in party and party["id"] == buyer_id:
            if "roles" in party and "buyer" in party["roles"]:
                result["result"] = True
                result["application_count"] = 1
                result["pass_count"] = 1
                result["meta"] = {
                    "party": party
                }

                return result

    result["result"] = False
    result["application_count"] = 1
    result["pass_count"] = 0
    result["meta"] = {
        "reason": "no organization with buyer role"
    }
    return result
