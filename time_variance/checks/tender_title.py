from tools.getter import get_values

version = 1.0


def filter(scope, item, item_id, new_item, new_item_id):
    # entry filtering - check makes sense only for tenders with a title filled in
    if item:
        values = get_values(item, "tender.title", value_only=True)
        if values:
            title = " ".join(values[0].lower().split())
            if title:
                return True

    return False


def evaluate(scope, item, item_id, new_item, new_item_id):
    values = get_values(item, "tender.title", value_only=True)
    if values:
        title = " ".join(values[0].lower().split())

        if new_item:
            new_values = get_values(new_item, "tender.title", value_only=True)

            new_title = None
            if new_values:
                new_title = " ".join(new_values[0].lower().split())

            if title == new_title:
                return scope, True
            else:
                return scope, False

    return scope, False
