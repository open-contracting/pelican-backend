from typing import Any, Callable, Dict, Optional, Tuple, Type


def get_empty_result_resource(version: float = 1.0) -> Dict[str, Any]:
    return {
        "result": None,
        "meta": None,
        "application_count": None,
        "pass_count": None,
        "version": version,
    }


def get_empty_result_dataset(version: float = 1.0) -> Dict[str, Any]:
    return {
        "result": None,
        "value": None,
        "meta": None,
        "version": version,
    }


def get_empty_result_time_variance(version: float = 1.0) -> Dict[str, Any]:
    return {
        "check_result": None,
        "check_value": None,
        "coverage_value": None,
        "coverage_result": None,
        "meta": None,
        "version": version,
    }


def get_empty_result_time_variance_scope() -> Dict[str, Any]:
    return {
        "total_count": 0,
        "coverage_count": 0,
        "failed_count": 0,
        "ok_count": 0,
        "examples": [],
    }


def field_coverage_check(
    name: str, test: Callable[[Dict[str, Any], str], Tuple[bool, str]], version: float = 1.0
) -> Callable[[Dict[str, Any], str], Dict[str, Any]]:
    """
    :param name: the machine name of the check
    :param test: a function that accepts a dict and a key and returns a tuple of a boolean (whether the test passed)
                 and a string (the reason for any failed test)
    :param version: the version number of the check
    """

    def method(item: Dict[str, Any], key: str) -> Dict[str, Any]:
        obj = _empty_field_result(name, version=version)

        if type(item) is not dict:
            passed, reason = False, f"ancestor is a {type(item).__name__}, not an object"
            value = item
        else:
            passed, reason = test(item, key)
            value = item.get(key)

        return _prepare_field_result(obj, passed, value, reason)

    return method


def field_quality_check(
    name: str,
    test: Callable[[Any], Tuple[bool, str]],
    version: float = 1.0,
    require_type: Optional[Type[Any]] = None,
    return_value: Optional[Callable[[Any], Any]] = None,
) -> Callable[[Dict[str, Any], str], Dict[str, Any]]:
    """
    :param name: the machine name of the check
    :param test: a function that accepts a value and returns a tuple of a boolean (whether the test passed) and a
                 string (the reason for any failed test)
    :param version: the version number of the check
    :param require_type: the type that the value must have for the test to run without error
    :param return_value: a function that accepts a value and returns the value to set in the returned object
    """

    def method(item: Dict[str, Any], key: str, **kwargs: Any) -> Dict[str, Any]:
        obj = _empty_field_result(name, version=version)

        value = item[key]

        if require_type and type(value) != require_type:
            obj["result"] = False
            obj["value"] = value
            obj["reason"] = f"not a {require_type.__name__}"
            return obj

        passed, reason = test(value, **kwargs)

        return _prepare_field_result(obj, passed, value, reason, return_value=return_value)

    return method


def _empty_field_result(name: str, version: float = 1.0) -> Dict[str, Any]:
    return {
        "name": name,
        "result": None,
        "value": None,
        "reason": None,
        "version": version,
    }


def _prepare_field_result(
    obj: Dict[str, Any], passed: bool, value: Any, reason: str, return_value: Optional[Callable[[Any], Any]] = None
) -> Dict[str, Any]:
    obj["result"] = passed
    if not passed:
        if return_value:
            obj["value"] = return_value(value)
        else:
            obj["value"] = value
        obj["reason"] = reason
    return obj
