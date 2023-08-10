import random
from collections.abc import Callable, Sequence
from typing import Any

from pelican.util.getter import parse_date


def get_empty_result_resource(version: float = 1.0) -> dict[str, Any]:
    """
    Initialize a compiled release-level check result.

    :param version: the check's version
    """
    return {
        "result": None,
        "meta": None,
        "application_count": None,
        "pass_count": None,
        "version": version,
    }


def get_empty_result_dataset(version: float = 1.0) -> dict[str, Any]:
    """
    Initialize a dataset-level check result.

    :param version: the check's version
    """
    return {
        "result": None,
        "value": None,
        "meta": None,
        "version": version,
    }


def get_empty_result_time_variance(version: float = 1.0) -> dict[str, Any]:
    """
    Initialize a time-based check result.

    :param version: the check's version
    """
    return {
        "check_result": None,
        "check_value": None,
        "coverage_value": None,
        "coverage_result": None,
        "meta": None,
        "version": version,
    }


def get_empty_result_time_variance_scope() -> dict[str, Any]:
    """
    Initialize a time-based check result accumulator.
    """
    return {
        "total_count": 0,
        "coverage_count": 0,
        "failed_count": 0,
        "ok_count": 0,
        "examples": [],
    }


def complete_result_resource(
    result: dict[str, Any],
    application_count: int,
    pass_count: int,
    reason: str | None = None,
    failed_paths: Sequence[str | dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build a compiled release-level check result.

    :param result: the check result
    :param application_count: the number of times the check was applied
    :param pass_count: the number of times the check passed
    :param reason: the reason to provide if the check was not applied
    :param failed_paths: the failed paths if the check failed
    """
    if reason and application_count == 0:
        result["meta"] = {"reason": reason}
        return result

    passed = application_count == pass_count

    result["result"] = passed
    result["application_count"] = application_count
    result["pass_count"] = pass_count

    if failed_paths and not passed:
        result["meta"] = {"failed_paths": failed_paths}

    return result


def complete_result_resource_pass_fail(
    result: dict[str, Any], passed: bool, meta: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Build a compiled release-level check result, for a pass-fail check.

    :param result: the check result
    :param passed: whether the check passed
    :param meta: the additional data to provide if the check failed
    """
    result["result"] = passed
    result["application_count"] = 1
    result["pass_count"] = int(passed)

    if meta and not passed:
        result["meta"] = meta

    return result


def field_coverage_check(
    name: str, test: Callable[[dict[str, Any], str], tuple[bool, str]], version: float = 1.0
) -> Callable[[dict[str, Any], str], dict[str, Any]]:
    """
    :param name: the machine name of the check
    :param test: a function that accepts a dict and a key and returns a tuple of a boolean (whether the test passed)
                 and a string (the reason for any failed test)
    :param version: the version number of the check
    """

    def method(item: dict[str, Any], key: str) -> dict[str, Any]:
        obj = _empty_field_result(name, version=version)

        # This is not a separate check, as checks ought to be able to assume the basic structure.
        if type(item) is not dict:
            passed, reason = False, f"parent is a {type(item).__name__}, not an object"
            value = item
        else:
            passed, reason = test(item, key)
            value = item.get(key)

        return _prepare_field_result(obj, passed, value, reason)

    return method


def field_quality_check(
    name: str,
    test: Callable[[Any], tuple[bool, str]],
    version: float = 1.0,
    require_type: type[Any] | None = None,
    return_value: Callable[[Any], Any] | None = None,
) -> Callable[[dict[str, Any], str], dict[str, Any]]:
    """
    :param name: the machine name of the check
    :param test: a function that accepts a value and returns a tuple of a boolean (whether the test passed) and a
                 string (the reason for any failed test)
    :param version: the version number of the check
    :param require_type: the type that the value must have for the test to run without error
    :param return_value: a function that accepts a value and returns the value to set in the returned object
    """

    def method(item: dict[str, Any], key: str, **kwargs: Any) -> dict[str, Any]:
        obj = _empty_field_result(name, version=version)

        value = item[key]

        if require_type and type(value) is not require_type:
            obj["result"] = False
            obj["value"] = value
            obj["reason"] = f"not a {require_type.__name__}"
            return obj

        passed, reason = test(value, **kwargs)

        return _prepare_field_result(obj, passed, value, reason, return_value=return_value)

    return method


def coherent_dates_check(version: float, pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    """
    Return a compiled release-level check result for coherent date pairs.

    A pair of dates is coherent if the first date is less than or equal to the second date.

    :param version: the check's version
    :param pairs: date value pairs
    """
    result = get_empty_result_resource(version)

    if not pairs:
        result["meta"] = {"reason": "no pairs of dates are set"}
        return result

    application_count = 0
    pass_count = 0
    failed_paths = []
    for first_date, second_date in pairs:
        first_date_parsed = parse_date(first_date["value"])
        second_date_parsed = parse_date(second_date["value"])

        if first_date_parsed is None or second_date_parsed is None:
            continue

        application_count += 1

        if first_date_parsed <= second_date_parsed:
            pass_count += 1
        else:
            failed_paths.append(
                {
                    "path_1": first_date["path"],
                    "value_1": first_date["value"],
                    "path_2": second_date["path"],
                    "value_2": second_date["value"],
                }
            )

    return complete_result_resource(
        result,
        application_count,
        pass_count,
        reason="no pairs of dates are parseable",
        failed_paths=failed_paths,
    )


def _empty_field_result(name: str, version: float = 1.0) -> dict[str, Any]:
    return {
        "name": name,
        "result": None,
        "value": None,
        "reason": None,
        "version": version,
    }


def _prepare_field_result(
    obj: dict[str, Any], passed: bool, value: Any, reason: str, return_value: Callable[[Any], Any] | None = None
) -> dict[str, Any]:
    obj["result"] = passed
    if not passed:
        if return_value:
            obj["value"] = return_value(value)
        else:
            obj["value"] = value
        obj["reason"] = reason
    return obj


class ReservoirSampler:
    def __init__(self, limit: int):
        if limit < 1:
            raise ValueError("limit must be a positive integer")

        self._limit = limit
        self._samples: list[Any] = []
        self._index = 0

    # https://en.wikipedia.org/wiki/Reservoir_sampling
    def process(self, value: Any) -> None:
        if self._index < self._limit:
            self._samples.append(value)
        else:
            r = random.randint(0, self._index)
            if r < self._limit:
                self._samples[r] = value

        self._index += 1

    def retrieve_samples(self) -> list[Any]:
        return self._samples
