
def get_empty_result_field(name, version=1.0):
    empty_result = {
        "name": name,
        "result": None,
        "value": None,
        "reason": None,
        "version": version
    }

    return empty_result


def get_empty_result_resource(version=1.0):
    empty_result = {
        "result": None,
        "value": None,
        "meta": None,
        "application_count": None,
        "pass_count": None,
        "version": version
    }

    return empty_result


def get_empty_result_dataset(version=1.0):
    empty_result = {
        "result": None,
        "value": None,
        "meta": None,
        "version": version
    }

    return empty_result
