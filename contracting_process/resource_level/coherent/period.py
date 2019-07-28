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
    for path in period_paths:
        periods = get_values(item, path)

        if not periods:
            continue

        for index in range(0, len(periods)):
            period = periods[index]["value"]

            # missing dates
            if "startDate" not in period or "endDate" not in period:
                continue

            # null dates
            if not period["startDate"] or not period["endDate"]:
                continue

            startDate = parse_datetime(period["startDate"])
            endDate = parse_datetime(period["endDate"])

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

            # initializing meta
            if not result["meta"]:
                result["meta"] = []

            # filling in the path of the processed period
            result["meta"].append({"path": "{}[{}]".format(path, index), "result": passed})

    result["application_count"] = application_count
    result["pass_count"] = pass_count

    if application_count is not None and pass_count is not None:
        result["result"] = application_count == pass_count
    else:
        result["meta"] = {"reason": "incomplete data for check"}

    return result
