"""
A compiled release in the newer collection has at least the same number of objects as its pair in the older collection.

The relevant objects are: ``planning``, ``tender``, ``awards`` entries and ``contracts`` entries.
"""

from pelican.util.getter import deep_get

version = 1.0


def applicable(scope, item, item_id, new_item, new_item_id):
    return True


def evaluate(scope, item, item_id, new_item, new_item_id):
    if deep_get(item, "tender", dict) and not deep_get(new_item, "tender", dict):
        return scope, False

    if deep_get(item, "planning", dict) and not deep_get(new_item, "planning", dict):
        return scope, False

    old_array = deep_get(item, "awards", list)
    if old_array:
        new_array = deep_get(new_item, "awards", list)
        if len(new_array) < len(old_array):
            return scope, False

    old_array = deep_get(item, "contracts", list)
    if old_array:
        new_array = deep_get(new_item, "contracts", list)
        if len(new_array) < len(old_array):
            return scope, False

    return scope, True
