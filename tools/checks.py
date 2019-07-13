def get_empty_result_resource(version):
    empty_result = {
        "result": None,
        "value": None,
        "meta": None,
        "application_count": None,
        "pass_count": None,
        "version": 1.0
    }

    empty_result["version"] = version
    return empty_result


def get_empty_result_dataset(version):
    empty_result = {
        "result": None,
        "value": None,
        "meta": None,
        "version": 1.0
    }

    empty_result["version"] = version
    return empty_result
