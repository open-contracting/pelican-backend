"""
If ``test_values`` is set, then each test value occurs in between 0.1% and 99% of cases.

Otherwise, no test is performed.
"""

from pelican.util.checks import ReservoirSampler, get_empty_result_dataset
from pelican.util.getter import get_values


class CodeDistribution:
    def __init__(self, paths, test_values=[], limit=20):
        self.paths = paths
        self.test_values = set(test_values)
        self.limit = limit

    def add_item(self, scope, item, item_id):
        ocid = item["ocid"]

        for path in self.paths:
            # Use get_values(), since path can be to either a string or a list of strings.
            for value in get_values(item, path, value_only=True):
                if type(value) is str:
                    scope.setdefault(value, ReservoirSampler(self.limit))
                    scope[value].process({"item_id": item_id, "ocid": ocid})

        return scope

    def get_result(self, scope):
        result = get_empty_result_dataset()

        if not scope:
            result["meta"] = {"reason": "no compiled releases set necessary fields"}
            return result

        total_count = sum(sampler.index for sampler in scope.values())
        passed = True
        shares = {}

        for code, sampler in scope.items():
            share = sampler.index / total_count
            if code in self.test_values:
                passed = passed and (0.001 <= share <= 0.99)
            shares[code] = {"count": sampler.index, "share": share, "examples": sampler.sample}

        # In other words, its share is 0%.
        if any(code not in scope for code in self.test_values):
            passed = False

        result["result"] = passed
        result["value"] = 100 if passed else 0
        result["meta"] = {"shares": shares}

        return result
