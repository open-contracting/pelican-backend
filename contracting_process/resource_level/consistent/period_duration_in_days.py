import math

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_get, get_values, parse_datetime

version = 1.0

SECONDS_PER_DAY = 24 * 60 * 60


def calculate(item):
    result = get_empty_result_resource(version)

    period_paths = [
        "tender.tenderPeriod",
        "tender.enquiryPeriod",
        "tender.awardPeriod",
        "tender.contractPeriod",
        "awards.contractPeriod",
        "contracts.period",
    ]

    periods = [period for path in period_paths for period in get_values(item, path)]

    application_count = 0
    pass_count = 0
    result["meta"] = {"periods": []}
    for period in periods:
        start_date = None
        if "startDate" in period["value"]:
            start_date = parse_datetime(period["value"]["startDate"])

        end_date = None
        if "endDate" in period["value"]:
            end_date = parse_datetime(period["value"]["endDate"])

        max_extent_day = None
        if "maxExtentDate" in period["value"]:
            max_extent_day = parse_datetime(period["value"]["maxExtentDate"])

        if "durationInDays" in period["value"]:
            duration_in_days = deep_get(period, "value.durationInDays", float)
        else:
            duration_in_days = None

        # this check cannot be applied
        if start_date is None or duration_in_days is None or (end_date is None and max_extent_day is None):
            continue

        passed = False
        if end_date is not None:
            duration_in_days_computed = (
                (end_date - start_date).days * SECONDS_PER_DAY + (end_date - start_date).seconds
            ) / SECONDS_PER_DAY
        else:
            duration_in_days_computed = (
                (max_extent_day - start_date).days * SECONDS_PER_DAY + (max_extent_day - start_date).seconds
            ) / SECONDS_PER_DAY

        passed = math.floor(duration_in_days_computed) <= duration_in_days <= math.ceil(duration_in_days_computed)

        application_count += 1
        if passed:
            pass_count += 1
        result["meta"]["periods"].append({"path": period["path"], "result": passed})

    return complete_result_resource(result, application_count, pass_count, reason="insufficient data for check")
