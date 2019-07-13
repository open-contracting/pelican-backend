import operator

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0


def add_item(scope, item, item_id):
    if type(item) == dict:
        values = get_values(item, "id")
        if values:
            for value in values:
                category = value["value"]

                if category not in scope:
                    scope[category] = {}
                    scope[category]["count"] = 0
                    scope[category]["examples"] = []

                scope[category]["count"] = scope[category]["count"] + 1
                if len(scope[category]["examples"]) < 100:
                    scope[category]["examples"].append(item_id)

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    if scope:
        max_item = max(scope.items(), key=lambda s: s[1]["count"])

        if max_item[1]["count"] > 1:
            data = {}

            items = sorted(scope.items(), key=lambda s: s[1]["count"])[:10]
            for item in items:
                if int(item[1]["count"]) > 1:
                    data[item[0]] = {}
                    data[item[0]]["count"] = int(item[1]["count"])
                    data[item[0]]["examples"] = item[1]["examples"]

            result["meta"] = {
                "failed": data
            }

            result["result"] = False
            result["value"] = 0
        else:
            result["result"] = True
            result["value"] = 100

        return result
    else:
        return result
