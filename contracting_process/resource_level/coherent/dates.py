from tools.checks import coherent_dates_check
from tools.getter import get_values

version = 1.0


def calculate(item):
    pairs = []

    for first_path, second_path in (
        ("tender.tenderPeriod.endDate", "tender.contractPeriod.startDate"),
        # ("tender.tenderPeriod.endDate", "date"),
        ("tender.tenderPeriod.endDate", "contracts.dateSigned"),
        ("contracts.dateSigned", "date"),
        ("tender.tenderPeriod.endDate", "awards.date"),
        ("awards.date", "date"),
    ):
        first_dates = get_values(item, first_path)
        second_dates = get_values(item, second_path)
        pairs.extend((first_date, second_date) for first_date in first_dates for second_date in second_dates)

    first_dates = get_values(item, "contracts.dateSigned")
    second_dates = get_values(item, "contracts.implementation.transactions.date")
    pairs.extend(
        (first_date, second_date)
        for first_date in first_dates
        for second_date in second_dates
        if first_date["path"].split(".", 1)[0] == second_date["path"].split(".", 1)[0]
    )

    awards = get_values(item, "awards")
    contracts = get_values(item, "contracts")
    pairs.extend(
        (
            {"path": f"{award['path']}.date", "value": award["value"]["date"]},
            {"path": f"{contract['path']}.dateSigned", "value": contract["value"]["dateSigned"]},
        )
        for award in awards
        if "date" in award["value"] and "id" in award["value"]
        for contract in contracts
        if "dateSigned" in contract["value"]
        and "awardID" in contract["value"]
        and str(award["value"]["id"]) == str(contract["value"]["awardID"])
    )

    return coherent_dates_check(version, pairs)
