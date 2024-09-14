"""
The tender title is invariant across time.

If a compiled release in the older collection sets the ``tender.title`` field, then its pair in the newer collection
has a matching ``tender.title`` field. Values are lowercased and whitespace-normalized for matching.
"""

from pelican.util.getter import deep_get

version = 1.0


def _get_title(item):
    if title := deep_get(item, "tender.title"):
        return " ".join(title.lower().split())
    return None


def applicable(scope, item, item_id, new_item, new_item_id):
    return bool(_get_title(item))


def evaluate(scope, item, item_id, new_item, new_item_id):
    return scope, _get_title(item) == _get_title(new_item)
