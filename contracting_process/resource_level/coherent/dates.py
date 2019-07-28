from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import parse_date

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)
    if not item:
        result["meta"] = {"reason": "insufficient data for check"}
        return result
    date_pairs_paths = [
        ["tender.tenderPeriod.endDate", "tender.contractPeriod.startDate"],
        ["tender.tenderPeriod.endDate", "date"],
        ["tender.tenderPeriod.endDate", "contracts.dateSigned"],
        ["contracts.dateSigned", "date"],
        ["tender.tenderPeriod.endDate", "awards.date"],
        ["awards.date", "date"]
    ]

    failed_paths = []
    result["application_count"] = 0
    result["pass_count"] = 0
    for date_pair_path in date_pairs_paths:
        first_dates = get_values(item, date_pair_path[0])
        second_dates = get_values(item, date_pair_path[1])

        if first_dates and second_dates:
            for first_date_item in first_dates:
                first_date = parse_date(first_date_item["value"])

                if first_date:
                    for second_date_item in second_dates:
                        second_date = parse_date(second_date_item["value"])

                        if second_date:
                            result["application_count"] = result["application_count"] + 1

                            if first_date > second_date:
                                failed_paths.append({
                                    "path_1": first_date_item["path"],
                                    "value_1": first_date_item["value"],
                                    "path_2": second_date_item["path"],
                                    "value_2": second_date_item["value"],
                                })
                            else:
                                result["pass_count"] = result["pass_count"] + 1

    same_size_date_pairs_paths = [
        ["awards.date", "contracts.dateSigned"]
    ]

    for date_pair_path in same_size_date_pairs_paths:
        first_dates = get_values(item, date_pair_path[0])
        second_dates = get_values(item, date_pair_path[1])

        if first_dates and second_dates and len(first_dates) == len(second_dates):
            for index in range(0, len(first_dates)):
                first_date = parse_date(first_dates[index]["value"])
                second_date = parse_date(second_dates[index]["value"])

                if first_date and second_date:
                    result["application_count"] = result["application_count"] + 1

                    if first_date > second_date:
                        failed_paths.append({
                            "path_1": "{}[{}]".format(first_dates[index]["path"]),
                            "value_1": first_dates[index]["value"],
                            "path_2": "{}[{}]".format(second_dates[index]["path"]),
                            "value_2": second_dates[index]["value"],
                        })
                    else:
                        result["pass_count"] = result["pass_count"] + 1

    if result["application_count"] == 0:
        result["application_count"] = None
        result["pass_count"] = None
        result["meta"] = {"reason": "insufficient data for check"}
        return result

    if result["application_count"] > result["pass_count"]:
        result["result"] = False
        result["meta"] = {
            "failed_paths": failed_paths
        }
    else:
        result["result"] = True

    return result
