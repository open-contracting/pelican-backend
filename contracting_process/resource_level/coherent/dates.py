from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values, parse_date

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)
    if not item:
        result["meta"] = {"reason": "insufficient data for check"}
        return result

    date_pairs_paths = [
        ["tender.tenderPeriod.endDate", "tender.contractPeriod.startDate"],
        # ["tender.tenderPeriod.endDate", "date"],
        ["tender.tenderPeriod.endDate", "contracts.dateSigned"],
        ["contracts.dateSigned", "date"],
        ["tender.tenderPeriod.endDate", "awards.date"],
        ["awards.date", "date"],
    ]

    application_count = 0
    pass_count = 0
    failed_paths = []
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
                            application_count += 1

                            if first_date > second_date:
                                failed_paths.append(
                                    {
                                        "path_1": first_date_item["path"],
                                        "value_1": first_date_item["value"],
                                        "path_2": second_date_item["path"],
                                        "value_2": second_date_item["value"],
                                    }
                                )
                            else:
                                pass_count += 1

    # special case for contracts[i].dateSined and contracts[i].implementation.transactions[j].date
    first_dates = get_values(item, "contracts.dateSigned")
    second_dates = get_values(item, "contracts.implementation.transactions.date")

    if first_dates and second_dates:
        for first_date_item in first_dates:
            first_date = parse_date(first_date_item["value"])

            if first_date:
                for second_date_item in second_dates:
                    if first_date_item["path"].split(".")[0] != second_date_item["path"].split(".")[0]:
                        continue

                    second_date = parse_date(second_date_item["value"])

                    if second_date:
                        application_count += 1

                        if first_date > second_date:
                            failed_paths.append(
                                {
                                    "path_1": first_date_item["path"],
                                    "value_1": first_date_item["value"],
                                    "path_2": second_date_item["path"],
                                    "value_2": second_date_item["value"],
                                }
                            )
                        else:
                            pass_count += 1

    # special case for awards[i].id = contracts[j].awardID
    if "awards" in item and "contracts" in item:
        awards = get_values(item, "awards")
        for award in awards:
            if "id" in award["value"] and "date" in award["value"]:
                award_id = award["value"]["id"]
                award_date = parse_date(award["value"]["date"])

                if not award_date or not award_id:
                    continue

                contracts = get_values(item, "contracts")
                for contract in contracts:
                    if "awardID" in contract["value"] and "dateSigned" in contract["value"]:
                        contract_id = contract["value"]["awardID"]
                        contract_date = parse_date(contract["value"]["dateSigned"])

                        if not contract_date or not contract_id or contract_id != award_id:
                            continue

                        application_count += 1

                        if award_date > contract_date:
                            failed_paths.append(
                                {
                                    "path_1": f"{award['path']}.date",
                                    "value_1": award["value"]["date"],
                                    "path_2": f"{contract['path']}.dateSigned",
                                    "value_2": contract["value"]["dateSigned"],
                                }
                            )
                        else:
                            pass_count += 1

    return complete_result_resource(
        result,
        application_count,
        pass_count,
        reason="insufficient data for check",
        meta={"failed_paths": failed_paths},
    )
