from collections import Counter

from tools.checks import get_empty_result_resource
from tools.getter import get_values


def calculate(item, path):
    result = get_empty_result_resource()
    result["application_count"] = 0
    result["pass_count"] = 0

    parties = [
        party
        for party in get_values(item, "parties")
        if ("id" in party["value"] and party["value"]["id"] and "name" in party["value"] and party["value"]["name"])
    ]
    party_id_counts = Counter([party["value"]["id"] for party in parties])

    parties_mapping = {}
    for party_id in party_id_counts:
        if party_id_counts[party_id] != 1:
            continue

        parties_mapping[party_id] = next(party for party in parties if party["value"]["id"] == party_id)

    if not parties_mapping:
        result["meta"] = {"reason": "there are no parties with unique id and name set"}
        return result

    test_values = [
        value
        for value in get_values(item, path)
        if ("id" in value["value"] and value["value"]["id"] and "name" in value["value"] and value["value"]["name"])
    ]

    result["meta"] = {"references": []}

    for value in test_values:
        if value["value"]["id"] not in parties_mapping:
            continue

        party = parties_mapping[value["value"]["id"]]

        passed = value["value"]["name"] == party["value"]["name"]
        result["application_count"] += 1
        if passed:
            result["pass_count"] += 1

        result["meta"]["references"].append(
            {
                "party": {"id": party["value"]["id"], "name": party["value"]["name"], "path": party["path"]},
                path: {"id": value["value"]["id"], "name": value["value"]["name"], "path": value["path"]},
                "result": passed,
            }
        )

    if result["application_count"] > 0:
        result["result"] = result["pass_count"] == result["application_count"]
    else:
        result["meta"] = {"reason": "there are no values with check-specific properties"}

    return result
