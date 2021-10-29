from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)
    if not item or "awards" not in item or "contracts" not in item:
        result["meta"] = {"reason": "insufficient data for check"}
        return result

    result["application_count"] = 0
    result["pass_count"] = 0

    awards = get_values(item, "awards")
    contracts = get_values(item, "contracts")

    failed_paths = []
    for contract in contracts:
        result["application_count"] += 1

        if not awards or len(awards) == 0:
            failed_paths.append(contract["path"])
            continue

        if "awardID" not in contract["value"]:
            failed_paths.append(contract["path"])
            continue

        awards_found_count = 0
        for award in awards:
            if (
                "id" in award["value"]
                and award["value"]["id"]
                and award["value"]["id"] == contract["value"]["awardID"]
            ):
                awards_found_count += 1

        if awards_found_count == 1:
            result["pass_count"] += 1
        else:
            failed_paths.append(contract["path"])

    if result["application_count"] == 0:
        result["application_count"] = None
        result["pass_count"] = None
        result["meta"] = {"reason": "insufficient data for check"}
        return result

    if result["application_count"] > result["pass_count"]:
        result["result"] = False
        result["meta"] = {"failed_paths": failed_paths}
    else:
        result["result"] = True

    return result
