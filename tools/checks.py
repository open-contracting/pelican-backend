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
        "value": None,
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
