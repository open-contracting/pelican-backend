"""
Coherence check for release date.

.. seealso::

   :func:`pelican.util.checks.coherent_dates_check
"""

from pelican.util.checks import coherent_dates_check
from pelican.util.getter import get_values

version = 1.0


def calculate(item):
    first_dates = []

    for first_path in (
        # amendments_dates
        "tender.amendments.date",
        "awards.amendments.date",
        "contracts.amendments.date",
        # dates
        "awards.date",
        "contracts.dateSigned",
        "contracts.implementation.transactions.date",
        # milestones_dates
        "planning.milestones.dateModified",
        "planning.milestones.dateMet",
        "tender.milestones.dateModified",
        "tender.milestones.dateMet",
        "contracts.milestones.dateModified",
        "contracts.milestones.dateMet",
        "contracts.implementation.milestones.dateModified",
        "contracts.implementation.milestones.dateMet",
        # documents_dates
        "planning.documents.datePublished",
        "planning.documents.dateModified",
        "tender.documents.datePublished",
        "tender.documents.dateModified",
        "awards.documents.datePublished",
        "awards.documents.dateModified",
        "contracts.documents.datePublished",
        "contracts.documents.dateModified",
        "contracts.implementation.documents.datePublished",
        "contracts.implementation.documents.dateModified",
    ):
        first_dates.extend(get_values(item, first_path))

    second_dates = get_values(item, "date")

    pairs = [(first_date, second_date) for first_date in first_dates for second_date in second_dates]

    return coherent_dates_check(version, pairs)
