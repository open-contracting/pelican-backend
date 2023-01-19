"""
.. seealso::

   :func:`tools.checks.coherent_dates_check
"""

from tools.checks import coherent_dates_check
from tools.getter import get_values

version = 1.0


def calculate(item):
    pairs = []

    for first_path, second_path in (
        ("tender.tenderPeriod.startDate", "tender.amendments.date"),
        ("tender.amendments.date", "date"),
        ("awards.amendments.date", "date"),
        ("contracts.amendments.date", "date"),
    ):
        first_dates = get_values(item, first_path)
        second_dates = get_values(item, second_path)
        pairs.extend((first_date, second_date) for first_date in first_dates for second_date in second_dates)

    for first_path, second_path in (
        ("awards.date", "awards.amendments.date"),
        ("contracts.dateSigned", "contracts.amendments.date"),
    ):
        first_dates = get_values(item, first_path)
        second_dates = get_values(item, second_path)
        pairs.extend(
            (first_date, second_date)
            for first_date in first_dates
            for second_date in second_dates
            if first_date["path"].split(".", 1)[0] == second_date["path"].split(".", 1)[0]
        )

    return coherent_dates_check(version, pairs)
