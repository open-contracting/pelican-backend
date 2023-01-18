from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values, parse_datetime

version = 1.0


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

    application_count = 0
    pass_count = 0
    failed_paths = []
    for path in period_paths:
        periods = get_values(item, path)

        if not periods:
            continue

        for period in periods:
            # missing dates
            if "startDate" not in period["value"] or "endDate" not in period["value"]:
                continue

            # null dates
            if not period["value"]["startDate"] or not period["value"]["endDate"]:
                continue

            startDate = parse_datetime(period["value"]["startDate"])
            endDate = parse_datetime(period["value"]["endDate"])

            # ill-formatted dates
            if not startDate or not endDate:
                continue

            passed = startDate <= endDate

            application_count += 1
            if passed:
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
