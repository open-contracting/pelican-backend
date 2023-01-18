from collections import Counter

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values


def calculate_path(item, path):
    result = get_empty_result_resource()

    party_id_counts = Counter(get_values(item, "parties.id", value_only=True))

    values = get_values(item, path)
    if not values:
        result["meta"] = {"reason": "insufficient data for check"}
        return result

    application_count = 0
    pass_count = 0
    failed_paths = []
    for value in values:
        application_count += 1

        if "id" not in value["value"]:
            failed_paths.append({"path": value["path"], "reason": "id missing"})
        elif value["value"]["id"] not in party_id_counts:
            failed_paths.append({"path": value["path"], "reason": "party with specified id is not present"})
        elif party_id_counts[value["value"]["id"]] > 1:
            failed_paths.append({"path": value["path"], "reason": "there are multiple parties with specified id"})
        else:
            pass_count += 1

    return complete_result_resource(result, application_count, pass_count, meta={"failed_paths": failed_paths})
