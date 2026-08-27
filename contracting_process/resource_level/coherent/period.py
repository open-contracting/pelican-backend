"""
Coherence check for period objects.

.. seealso::

   :func:`pelican.util.checks.coherent_dates_check
"""

from pelican.util.checks import coherent_dates_check
from pelican.util.getter import get_values
from pelican.util.schema import get_paths

version = 1.0
paths = tuple((f"{path}.startDate", f"{path}.endDate") for path in get_paths("Period"))


def calculate(item):
    pairs = []

    for first_path, second_path in paths:
        first_dates = get_values(item, first_path)
        second_dates = get_values(item, second_path)
        pairs.extend(
            (first_date, second_date)
            for first_date in first_dates
            for second_date in second_dates
            if first_date["path"].rsplit(".", 1)[0] == second_date["path"].rsplit(".", 1)[0]  # `split` not needed
        )

    return coherent_dates_check(version, pairs)
