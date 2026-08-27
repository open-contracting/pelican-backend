"""
Coherence check for release date.

.. seealso::

   :func:`pelican.util.checks.coherent_dates_check
"""

from pelican.util.checks import coherent_dates_check
from pelican.util.getter import get_values
from pelican.util.schema import get_paths

version = 1.0
paths = (
    "awards.date",
    "contracts.dateSigned",
    "contracts.implementation.transactions.date",
    *(f"{path}.date" for path in get_paths("Amendment")),
    *(f"{path}.{key}" for path in get_paths("Milestone") for key in ("dateModified", "dateMet")),
    *(f"{path}.{key}" for path in get_paths("Document") for key in ("datePublished", "dateModified")),
)


def calculate(item):
    first_dates = [value for path in paths for value in get_values(item, path)]

    second_dates = get_values(item, "date")

    pairs = [(first_date, second_date) for first_date in first_dates for second_date in second_dates]

    return coherent_dates_check(version, pairs)
