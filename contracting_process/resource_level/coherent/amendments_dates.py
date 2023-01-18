from tools.checks import complete_result_resource, get_empty_result_resource
from tools.getter import get_values, parse_date

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    pairs = []
    pairs.extend(
        (first_date, second_date)
        for first_date in get_values(item, "tender.tenderPeriod.startDate")
        for second_date in get_values(item, "tender.amendments.date")
    )
    pairs.extend(
        (first_date, second_date)
        for first_date in get_values(item, "tender.amendments.date")
        for second_date in get_values(item, "date")
    )
    pairs.extend(
        (first_date, second_date)
        for first_date in get_values(item, "awards.date")
        for second_date in get_values(item, "awards.amendments.date")
        if first_date["path"].split(".")[0] == second_date["path"].split(".")[0]
    )
    pairs.extend(
        (first_date, second_date)
        for first_date in get_values(item, "awards.amendments.date")
        for second_date in get_values(item, "date")
    )
    pairs.extend(
        (first_date, second_date)
        for first_date in get_values(item, "contracts.dateSigned")
        for second_date in get_values(item, "contracts.amendments.date")
        if first_date["path"].split(".")[0] == second_date["path"].split(".")[0]
    )
    pairs.extend(
        (first_date, second_date)
        for first_date in get_values(item, "contracts.amendments.date")
        for second_date in get_values(item, "date")
    )

    application_count = 0
    pass_count = 0
    failed_paths = []
    for first_date, second_date in pairs:
        first_date_parsed = parse_date(first_date["value"])
        second_date_parsed = parse_date(second_date["value"])

        if first_date_parsed is None or second_date_parsed is None:
            continue

        application_count += 1

        if first_date_parsed <= second_date_parsed:
            pass_count += 1
        else:
            failed_paths.append(
                {
                    "path_1": first_date["path"],
                    "value_1": first_date["value"],
                    "path_2": second_date["path"],
                    "value_2": second_date["value"],
                }
            )

    return complete_result_resource(
        result,
        application_count,
        pass_count,
        reason="insufficient data for check",
        meta={"failed_paths": failed_paths},
    )
