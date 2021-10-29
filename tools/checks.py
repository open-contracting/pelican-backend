def get_empty_result_field(name, version=1.0):
    return {
        "name": name,
        "result": None,
        "value": None,
        "reason": None,
        "version": version,
    }


def get_empty_result_resource(version=1.0):
    return {
        "result": None,
        "meta": None,
        "application_count": None,
        "pass_count": None,
        "version": version,
    }


def get_empty_result_dataset(version=1.0):
    return {
        "result": None,
        "value": None,
        "meta": None,
        "version": version,
    }


def get_empty_result_time_variance(version=1.0):
    return {
        "check_result": None,
        "check_value": None,
        "coverage_value": None,
        "coverage_result": None,
        "meta": None,
        "version": version,
    }


def get_empty_result_time_variance_scope():
    return {
        "total_count": 0,
        "coverage_count": 0,
        "failed_count": 0,
        "ok_count": 0,
        "examples": [],
    }


def field_level_check(name, func, require_type=None):
    def method(item, key):
        result = get_empty_result_field(name)

        value = item[key]
        if require_type and type(value) != require_type:
            result["result"] = False
            result["value"] = value
            result["reason"] = f"not a {require_type.__name__}"

            return result

        passed, reason = func(value)

        result["result"] = passed
        if not passed:
            result["value"] = value
            if not result["reason"]:
                result["reason"] = reason

        return result

    return method
