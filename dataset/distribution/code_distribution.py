from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import get_values


class CodeDistribution:
    def __init__(self, paths, test_values=[], limit=20):
        self.paths = paths
        self.test_values = set(test_values)
        self.limit = limit

    def add_item(self, scope, item, item_id):
        ocid = get_values(item, "ocid", value_only=True)[0]

        values = []
        for path in self.paths:
            values.extend(get_values(item, path, value_only=True))

        for value in values:
            if value is None or not isinstance(value, str):
                continue

            scope.setdefault(
                value,
                {
                    "count": 0,
                    "sampler": ReservoirSampler(self.limit),
                },
            )
            scope[value]["count"] += 1
            scope[value]["sampler"].process({"item_id": item_id, "ocid": ocid})

        return scope

    def get_result(self, scope):
        result = get_empty_result_dataset()

        if not scope:
            result["meta"] = {"reason": "no compiled releases set necessary fields"}
            return result

        total_count = sum(value["count"] for value in scope.values())

        passed = True
        for key, value in scope.items():
            value["share"] = value["count"] / total_count
            value["examples"] = value["sampler"].sample
            del value["sampler"]

            if key in self.test_values:
                passed = passed and (0.001 <= value["share"] <= 0.99)

        if any(key not in scope for key in self.test_values):
            passed = False

        result["result"] = passed
        result["value"] = 100 if passed else 0
        result["meta"] = {"shares": scope}

        return result
