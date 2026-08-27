"""If a milestone's ``status`` is unmet ('scheduled' or 'notMet'), then its ``dateMet`` is blank."""

from pelican.util.checks import complete_result_resource, get_empty_result_resource
from pelican.util.getter import deep_get, get_values
from pelican.util.schema import get_paths

version = 1.0
applicable_statuses = {"scheduled", "notMet"}
paths = get_paths("Milestone")


def calculate(item):
    result = get_empty_result_resource(version)

    milestones = [
        value
        for path in paths
        for value in get_values(item, path)
        if deep_get(value["value"], "status") in applicable_statuses
    ]

    if not milestones:
        result["meta"] = {"reason": "no milestone is unmet"}
        return result

    application_count = 0
    pass_count = 0
    failed_paths = []
    for milestone in milestones:
        passed = not deep_get(milestone["value"], "dateMet")

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append({"path": milestone["path"], "status": milestone["value"]["status"]})

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
