"""
Coherence check for document dates.

.. seealso::

   :func:`pelican.util.checks.coherent_dates_check
"""

from functools import lru_cache

from pelican.util.checks import coherent_dates_check
from pelican.util.getter import get_values
from pelican.util.schema import get_paths

version = 1.0
paths = tuple(
    triple
    for path in get_paths("Document")
    for triple in (
        (f"{path}.datePublished", f"{path}.dateModified", True),
        (f"{path}.datePublished", "date", False),
        (f"{path}.dateModified", "date", False),
    )
)


def calculate(item):
    @lru_cache
    def _get_values(path):
        return get_values(item, path)

    pairs = []

    for first_path, second_path, split in paths:
        first_dates = _get_values(first_path)
        second_dates = _get_values(second_path)
        pairs.extend(
            (first_date, second_date)
            for first_date in first_dates
            for second_date in second_dates
            if not split or first_date["path"].rsplit(".", 1)[0] == second_date["path"].rsplit(".", 1)[0]
        )

    return coherent_dates_check(version, pairs)
