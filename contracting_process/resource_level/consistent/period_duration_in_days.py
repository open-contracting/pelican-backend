import math

from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import parse_datetime

version = 1.0


def calculate(item, path):
    """Method is designed to test items for correct periods - if period duration is consistent with start and enddate.

    Parameters
    ------------
    item: dict
        testing JSON
    path:
        path to the tested period


    Returns
    -----------
    result: dict
        {
            "result" - if successed
            "application_count" - application count
            "pass_count" - pass count
            "meta" -
                "periods" -
                    "path"  - path to the tested role
                    "result" - if successed
        }

    """

    result = get_empty_result_resource(version)

    periods = [period for period in get_values(item, path)]

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

        duration_in_days = period["value"]["durationInDays"] if "durationInDays" in period["value"] else None

        # this check cannot be applied
        if start_date is None or duration_in_days is None or (end_date is None and max_extent_day is None):
            continue

        passed = False
        if end_date is not None:
            duration_in_days_computed = (
                (end_date - start_date).days * 24 * 60 * 60 + (end_date - start_date).seconds
            ) / (24 * 60 * 60)
        else:
            duration_in_days_computed = (
                (max_extent_day - start_date).days * 24 * 60 * 60 + (max_extent_day - start_date).seconds
            ) / (24 * 60 * 60)

        passed = math.floor(duration_in_days_computed) <= duration_in_days <= math.ceil(duration_in_days_computed)

        result["application_count"] += 1
        result["pass_count"] = result["pass_count"] + 1 if passed else result["pass_count"]
        result["meta"]["periods"].append({"path": period["path"], "result": passed})

    if result["application_count"] == 0:
        result["application_count"] = None
        result["pass_count"] = None
        result["meta"] = {"reason": "there are no values with check-specific properties"}
    else:
        result["result"] = result["application_count"] == result["pass_count"]

    return result
