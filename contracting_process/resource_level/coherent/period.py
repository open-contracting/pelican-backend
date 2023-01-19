"""
.. seealso::

   :func:`tools.checks.coherent_dates_check
"""

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values, parse_datetime

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    periods = []
    for path in (
        "tender.tenderPeriod",
        "tender.enquiryPeriod",
        "tender.awardPeriod",
        "tender.contractPeriod",
        "awards.contractPeriod",
        "contracts.period",
    ):
        periods.extend(
            period
            for period in get_values(item, path)
            if "startDate" in period["value"] and "endDate" in period["value"]
        )

    if not periods:
        result["meta"] = {"reason": "no pairs of dates in periods are set"}
        return result

    application_count = 0
    pass_count = 0
    failed_paths = []
    for period in periods:
        first_date_parsed = parse_datetime(period["value"]["startDate"])
        second_date_parsed = parse_datetime(period["value"]["endDate"])

        if first_date_parsed is None or second_date_parsed is None:
            continue

        application_count += 1

        if first_date_parsed <= second_date_parsed:
            pass_count += 1
        else:
            failed_paths.append(period["path"])

    return complete_result_resource(
        result,
        application_count,
        pass_count,
        reason="insufficient data for check",
        meta={"failed_paths": failed_paths},
    )
