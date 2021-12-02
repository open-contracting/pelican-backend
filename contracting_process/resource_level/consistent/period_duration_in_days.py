import math

from tools.checks import get_empty_result_resource
from tools.getter import deep_get, get_values
from tools.helpers import parse_datetime

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

    result["application_count"] = 0
    result["pass_count"] = 0
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

        result["application_count"] += 1
        if passed:
            result["pass_count"] += 1
        result["meta"]["periods"].append({"path": period["path"], "result": passed})

    if result["application_count"] == 0:
        result["application_count"] = None
        result["pass_count"] = None
        result["meta"] = {"reason": "there are no values with check-specific properties"}
    else:
        result["result"] = result["application_count"] == result["pass_count"]

    return result
