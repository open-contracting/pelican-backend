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

    # special case for awards[i].id = contracts[j].awardID
    awards = get_values(item, "awards")[0]["value"]
    for award_index in range(0, len(awards)):
        award = awards[award_index]

        if "id" in award and "date" in award:
            award_id = award["id"]
            award_date = parse_date(award["date"])

            if not award_date or not award_id:
                continue

            contracts = get_values(item, "contracts")[0]["value"]
            for contract_index in range(0, len(contracts)):
                contract = contracts[contract_index]
                if "awardID" in contract and "dateSigned" in contract:
                    contract_id = contract["awardID"]
                    contract_date = parse_date(contract["dateSigned"])

                    if not contract_date or not contract_id or contract_id != award_id:
                        continue

                    result["application_count"] = result["application_count"] + 1

                    if award_date > contract_date:
                        failed_paths.append({
                            "path_1": "awards[{}].date".format(award_index),
                            "value_1": award["date"],
                            "path_2": "contracts[{}].dateSigned".format(contract_index),
                            "value_2": contract["dateSigned"],
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
