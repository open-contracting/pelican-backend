def get_empty_result(version):
    empty_result = {
        "result": None,
        "value": 0,
        "meta": None,
        "application_count": None,
        "pass_count": None,
        "version": 1.0
    }

    empty_result["version"] = version
    return empty_result
