from tools.checks import coherent_dates_check
from tools.getter import get_values

version = 1.0


def calculate(item):
    first_dates, second_dates = [], get_values(item, "date")

    for path in (
        "planning.milestones.dateModified",
        "planning.milestones.dateMet",
        "tender.milestones.dateModified",
        "tender.milestones.dateMet",
        "contracts.milestones.dateModified",
        "contracts.milestones.dateMet",
        "contracts.implementation.milestones.dateModified",
        "contracts.implementation.milestones.dateMet",
    ):
        first_dates.extend(get_values(item, path))

    pairs = [(first_date, second_date) for first_date in first_dates for second_date in second_dates]

    return coherent_dates_check(version, pairs)
