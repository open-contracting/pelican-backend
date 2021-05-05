from collections import Counter

from tools.checks import get_empty_result_resource
from tools.getter import get_values


def calculate_path(item, path):
    result = get_empty_result_resource()
    result["application_count"] = 0
    result["pass_count"] = 0

    party_id_counts = Counter(get_values(item, "parties.id", value_only=True))

    values = get_values(item, path)
    if not values:
        result["meta"] = {"reason": "there are no values with check-specific properties"}
        return result

    result["meta"] = {"failed": []}

    for value in values:
        result["application_count"] += 1

        if "id" not in value["value"]:
            result["meta"]["failed"].append({"path": value["path"], "reason": "id missing"})
        elif value["value"]["id"] not in party_id_counts:
            result["meta"]["failed"].append(
                {"path": value["path"], "reason": "party with specified id is not present"}
            )
        elif party_id_counts[value["value"]["id"]] > 1:
            result["meta"]["failed"].append(
                {"path": value["path"], "reason": "there are multiple parties with specified id"}
            )
        else:
            result["pass_count"] += 1

    result["result"] = result["pass_count"] == result["application_count"]

    return result
