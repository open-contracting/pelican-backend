"""
For each period, ``durationInDays`` is equal to the difference between ``startDate`` and ``endDate``. If ``endDate`` is
blank or unparsable, then ``durationInDays`` is equal to the difference between ``startDate`` and ``maxExtentDate``.

Since the test operates on all period objects, the test silently ignores any dates that can't be parsed.
"""

import datetime
import math

from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import deep_get, get_values

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
        periods.extend(get_values(item, path))

    application_count = 0
    pass_count = 0
    failed_paths = []
    for period in periods:
        start_date = deep_get(period["value"], "startDate", datetime.datetime)
        end_date = deep_get(period["value"], "endDate", datetime.datetime)
        max_extent_date = deep_get(period["value"], "maxExtentDate", datetime.datetime)
        duration_in_days = deep_get(period, "value.durationInDays", float)

        if start_date is None or duration_in_days is None or (end_date is None and max_extent_date is None):
            continue

        delta = (end_date if end_date is not None else max_extent_date) - start_date
        expected = delta.days + delta.seconds / 86400  # seconds per day
        passed = math.floor(expected) <= duration_in_days <= math.ceil(expected)

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append(period["path"])

    return complete_result_resource(
        result,
        application_count,
        pass_count,
        reason="no period has a valid start date and valid end date",
        failed_paths=failed_paths,
    )
