import sys
import time

from psycopg2.extras import Json

from contracting_process.field_level.definitions import \
    definitions as field_level_definitions
from contracting_process.resource_level.definitions import \
    definitions as resource_level_definitions
from tools.db import commit, get_cursor
from tools.getter import get_value


def do_work(data, item_id, dataset_id):
    field_level_checks(data, item_id, dataset_id)

    resource_level_checks(data, item_id, dataset_id)

    commit()

    sys.exit()

    return None


def resource_level_checks(data, item_id, dataset_id):
    # perform resource level checks
    for check_name, checks in resource_level_definitions.items():
        # confront value with its checks
        for check in checks:
            check_result = check(value, path_chunks[-1])
            if not check_result["result"]:
                break


def field_level_checks(data, item_id, dataset_id):
    # perform field level checks
    for path, checks in field_level_definitions.items():
        # get the parent/parents
        path_chunks = path.split(".")

        value = {}
        if (len(path_chunks) > 1):
            # dive deeper in tree
            value = get_value(data, path_chunks[:-1])
        else:
            # checking top level item
            value = data

        # "norm" value for iterations
        if type(value) is not list:
            values = [value]
        else:
            values = value

        # iterate over parents and perform checks
        for value in values:
            check_result = {}

            # confront value with its checks
            for check in checks:
                check_result = check(value, path_chunks[-1])
                if not check_result["result"]:
                    break

            # save result
            save_field_level_check(path, check_result, item_id, dataset_id)


def save_field_level_check(path, result, item_id, dataset_id):
    cursor = get_cursor()

    if "reason" in result:
        meta = Json({"reason": result["reason"], "value": result["value"]})
    else:
        meta = None

    cursor.execute("""
        INSERT INTO field_level_check
        (path, result, meta, data_item_id, dataset_id, created, modified)
        VALUES
        (%s, %s, %s, %s, %s, now(), now())
        """, (
        path,
        result["result"],
        meta,
        item_id,
        dataset_id)
    )
