from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)
    if not item or "awards" not in item or "contracts" not in item:
        result["meta"] = {"reason": "insufficient data for check"}
        return result

    application_count = 0
    pass_count = 0

    awards = get_values(item, "awards")
    contracts = get_values(item, "contracts")

    failed_paths = []
    for contract in contracts:
        application_count += 1

        if not awards:
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
            pass_count += 1
        else:
            failed_paths.append(contract["path"])

    return complete_result_resource(
        result,
        application_count,
        pass_count,
        reason="insufficient data for check",
        meta={"failed_paths": failed_paths},
    )
