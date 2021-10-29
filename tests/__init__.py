import json
import os


def is_subset_dict(subset, superset):
    return subset.items() <= superset.items()


def read(basename):
    with open(os.path.join("tests", "fixtures", f"{basename}.json")) as f:
        return json.load(f)


# I'm not sure if this can be accomplished with pytest, so using unittest with pytest-subtests. At first glance, we
# would need to auto-generate parametrized `test_` functions, with the module as a bound variable.


class FieldCoverageTests:
    def test_passing(self):
        # Ensure the child class is configured.
        assert self.passing

        for item in self.passing:
            with self.subTest(item=item):
                result = self.module.calculate(item, "key")

                self.assertEqual(
                    result,
                    {
                        "name": self.module.name,
                        "result": True,
                        "value": None,
                        "reason": None,
                        "version": 1.0,
                    },
                )

    def test_failing(self):
        # Ensure the child class is configured.
        assert self.failing

        for params in self.failing:
            item = params[0]
            reason = params[1]
            if len(params) > 2:
                return_value = params[2]
            else:
                return_value = None

            with self.subTest(item=item):
                result = self.module.calculate(item, "key")

                self.assertEqual(
                    result,
                    {
                        "name": self.module.name,
                        "result": False,
                        "value": return_value,
                        "reason": reason,
                        "version": 1.0,
                    },
                )


class FieldQualityTests:
    passing_kwargs = {}
    failing_kwargs = {}
    method = "calculate"

    def setUp(self):
        self.method = getattr(self.module, self.method)

    def test_passing(self):
        for value in self.passing:
            with self.subTest(value=value):
                # raise Exception(repr(self.method))
                result = self.method({"xxx": value}, "xxx", **self.passing_kwargs)

                self.assertEqual(
                    result,
                    {
                        "name": self.module.name,
                        "result": True,
                        "value": None,
                        "reason": None,
                        "version": 1.0,
                    },
                )

    def test_failing(self):
        for params in self.failing:
            value = params[0]
            reason = params[1]
            if len(params) > 2:
                return_value = params[2]
            else:
                return_value = value

            with self.subTest(value=value):
                result = self.method({"xxx": value}, "xxx", **self.failing_kwargs)

                self.assertEqual(
                    result,
                    {
                        "name": self.module.name,
                        "result": False,
                        "value": return_value,
                        "reason": reason,
                        "version": 1.0,
                    },
                )
