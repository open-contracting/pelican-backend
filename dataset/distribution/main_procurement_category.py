from pelican.util.checks import get_empty_result_dataset
from pelican.util.getter import get_values

version = 1.0


def add_item(scope, item, item_id):
    ocid = get_values(item, "ocid", value_only=True)[0]

    categories = get_values(item, "tender.mainProcurementCategory", value_only=True)
    if categories:
        for category in categories:
            scope.setdefault(
                category,
                {
                    "count": 0,
                    "examples": [],
                },
            )
            scope[category]["count"] += 1
            if len(scope[category]["examples"]) < 100:
                scope[category]["examples"].append({"item_id": item_id, "ocid": ocid})

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if scope:
        sorted_scope = sorted(scope.items(), key=lambda item: item[1]["count"])
        total_count = sum(value["count"] for _, value in sorted_scope)

        result["meta"] = {
            "shares": {
                category: {
                    "share": value["count"] / total_count,
                    "count": value["count"],
                    "examples": value["examples"],
                }
                for category, value in sorted_scope
            }
        }

        passed = sorted_scope[-1][1]["count"] / total_count <= 0.95

        result["result"] = passed
        result["value"] = 100 if passed else 0

        return result
    else:
        return result
