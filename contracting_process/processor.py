import sys
import time

from contracting_process.field_level.definitions import field_level_definitions
from tools.getter import get_value


def do_work(data, item_id, dataset_id):
    print(data)

    for path, checks in definitions.items():
        path = path.split(".")

        value = data
        if (len(path) > 1):
            value = get_value(data, path[1:])

        print(value)

        # execute plugin
        for check in checks:
            result = check(value)

        print(result)
        # save result
        save_field_level_check(plugin_name, result)

        sys.exit()

    return None


def save_field_level_check(path, result, item_id, dataset_id):
    cursor = get_cursor()
    cursor.execute("""
        INSERT INTO field_level_check
        (path, result, meta, data_item_id, dataset_id, created, modified)
        VALUES
        (%s, %s, %s, %s, %s, now(), now())
        """, (
        plugin_name,
        result["result"],
        result["meta"],
        item_id,
        dataset_id)
    )
