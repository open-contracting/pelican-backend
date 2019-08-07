from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import parse_datetime

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    period_paths = ["tender.tenderPeriod",
                    "tender.enquiryPeriod",
                    "tender.awardPeriod",
                    "tender.contractPeriod",
                    "awards.contractPeriod",
                    "contracts.period"]

    application_count = None
    pass_count = None
    failed_paths = []
    for path in period_paths:
        periods = get_values(item, path)

        if not periods:
            continue

        for period in periods:
            # missing dates
            if "startDate" not in period["value"] or \
                    "endDate" not in period["value"]:
                continue

            # null dates
            if not period["value"]["startDate"] or \
                    not period["value"]["endDate"]:
                continue

            startDate = parse_datetime(period["value"]["startDate"])
            endDate = parse_datetime(period["value"]["endDate"])

            # ill-formatted dates
            if not startDate or not endDate:
                continue

            passed = startDate <= endDate

            if application_count is not None:
                application_count += 1
            else:
                application_count = 1

            if pass_count is not None:
                pass_count = pass_count + 1 if passed else pass_count
            else:
                pass_count = 1 if passed else 0

            failed_paths.append({"path": period["path"], "result": passed})

    result["application_count"] = application_count
    result["pass_count"] = pass_count
    if application_count is not None and pass_count is not None:
        result["result"] = application_count == pass_count
    else:
        result["meta"] = {"reason": "incomplete data for check"}
    if failed_paths:
        result["meta"] = {"failed_paths": failed_paths}
    return result
