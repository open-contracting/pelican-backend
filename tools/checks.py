def get_empty_result_field(name, version=1.0):
    empty_result = {"name": name, "result": None, "value": None, "reason": None, "version": version}

    return empty_result


def get_empty_result_resource(version=1.0):
    empty_result = {
        "result": None,
        "value": None,
        "meta": None,
        "application_count": None,
        "pass_count": None,
        "version": version,
    }

    return empty_result


def get_empty_result_dataset(version=1.0):
    empty_result = {"result": None, "value": None, "meta": None, "version": version}

    return empty_result


def get_empty_result_time_variance(version=1.0):
    empty_result = {
        "check_result": None,
        "check_value": None,
        "coverage_value": None,
        "coverage_result": None,
        "meta": None,
        "version": version,
    }

    return empty_result


def get_empty_result_time_variance_scope():
    scope = {}
    scope["total_count"] = 0
    scope["coverage_count"] = 0
    scope["failed_count"] = 0
    scope["ok_count"] = 0
    scope["examples"] = []
    return scope
