version = 1.0


def filter(scope, item, item_id, new_item, new_item_id):
    # entry filtering - check makes sense for all the items
    if item:
        return True

    return False


def evaluate(scope, item, item_id, new_item, new_item_id):
    # `time_variance/processor.py` currently tests whether `new_item` is truthy before calling `evaluate`, and the
    # `filter` function above tests whether `item` is truthy, such that this function will always return `True`.
    # Nonetheless, the code is preserved in case the logic in `time_variance/processor.py` is changed.
    if item and new_item:
        return scope, True

    return scope, False
