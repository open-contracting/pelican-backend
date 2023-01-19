import json
import os
from contextlib import AbstractContextManager

from pelican.util import settings


def is_subset_dict(subset, superset):
    return subset.items() <= superset.items()


def read(basename):
    with open(os.path.join("tests", "fixtures", f"{basename}.json")) as f:
        return json.load(f)


class override_settings(AbstractContextManager):
    def __init__(self, **kwargs):
        self.new = kwargs
        self.old = {}

        for key, value in self.new.items():
            self.old[key] = getattr(settings, key)

    def __enter__(self):
        for key, value in self.new.items():
            setattr(settings, key, value)

    def __exit__(self, *args):
        for key, value in self.old.items():
            setattr(settings, key, value)


# I'm not sure if the below can be accomplished with pytest, so using unittest with pytest-subtests. At first glance,
# we would need to auto-generate parametrized `test_` functions, with the module as a bound variable.


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


class CompiledReleaseTests:
    maxDiff = None
    passing_kwargs = {}
    failing_kwargs = {}
    method = "calculate"

    def setUp(self):
        self.method = getattr(self.module, self.method)

    def test_skipping(self):
        skipping = self.skipping
        skipping.append(({}, skipping[0][1]))
        for item, reason in skipping:
            with self.subTest(item=item):
                result = self.method(item, **self.passing_kwargs)

                self.assertEqual(
                    result,
                    {
                        "result": None,
                        "meta": {"reason": reason},
                        "application_count": None,
                        "pass_count": None,
                        "version": 1.0,
                    },
                )

    def test_passing(self):
        for item, meta, count in self.passing:
            with self.subTest(item=item):
                result = self.method(item, **self.passing_kwargs)

                self.assertEqual(
                    result,
                    {
                        "result": True,
                        "meta": meta,
                        "application_count": count,
                        "pass_count": count,
                        "version": 1.0,
                    },
                )

    def test_failing(self):
        for item, meta, application_count, pass_count in self.failing:
            with self.subTest(item=item):
                result = self.method(item, **self.failing_kwargs)

                self.assertEqual(
                    result,
                    {
                        "result": False,
                        "meta": meta,
                        "application_count": application_count,
                        "pass_count": pass_count,
                        "version": 1.0,
                    },
                )
