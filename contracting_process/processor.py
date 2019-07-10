import sys
import time
from random import randrange

from psycopg2.extras import Json

from contracting_process.field_level.definitions import \
    definitions as field_level_definitions
from contracting_process.resource_level.definitions import \
    definitions as resource_level_definitions
from tools.db import commit, get_cursor
from tools.getter import get_values


def do_work(data, item_id, dataset_id):
    field_level_checks(data, item_id, dataset_id)

    resource_level_checks(data, item_id, dataset_id)

    commit()

    if randrange(50) > 40:
        sys.exit()

    return None


def resource_level_checks(data, item_id, dataset_id):
    # perform resource level checks
    for check_name, checks in resource_level_definitions.items():
        # confront value with its checks
        for check in checks:
            check_result = check(data)
            save_resource_level_check(check_name, check_result, item_id, dataset_id)


def field_level_checks(data, item_id, dataset_id):
    # perform field level checks
    for path, checks in field_level_definitions.items():
        # get the parent/parents
        path_chunks = path.split(".")

        values = []
        if (len(path_chunks) > 1):
            # dive deeper in tree
            values = get_values(data, ".".join(path_chunks[:-1]))
        else:
            # checking top level item
            values = [{"path": "", "value": data}]

        if values:
            # iterate over parents and perform checks
            for value in values:
                list_result = True

                # create list from plain values
                if type(value["value"]) is dict:
                    value["value"] = [value["value"]]
                    list_result = False

                # iterate over all returned values and check those
                counter = 0
                for item in value["value"]:
                    check_result = {}

                    # confront value with its checks
                    for check in checks:
                        check_result = check(item, path_chunks[-1])
                        if not check_result["result"]:
                            break

                    # construct path based on "is the parent a list?"
                    if list_result:
                        check_result["path"] = "{}[{}].{}".format(value["path"], counter, path_chunks[-1])
                    else:
                        if value["path"]:
                            check_result["path"] = "{}.{}".format(value["path"], path_chunks[-1])
                        else:
                            check_result["path"] = path_chunks[-1]

                    counter = counter + 1

                    # save result
                    save_field_level_check(path, check_result, item_id, dataset_id)


def save_field_level_check(path, result, item_id, dataset_id):
    cursor = get_cursor()

    if "reason" in result:
        meta = Json({"reason": result["reason"], "value": result["value"], "path": result["path"]})
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


def save_resource_level_check(check_name, result, item_id, dataset_id):
    cursor = get_cursor()

    result["meta"]["version"] = result["version"]
    meta = Json(result["meta"])

    cursor.execute("""
        INSERT INTO resource_level_check
        (check_name, result, pass_count, application_count, meta, data_item_id, dataset_id, created, modified)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, now(), now())
        """, (
        check_name,
        result["result"],
        result["pass_count"],
        result["application_count"],
        meta,
        item_id,
        dataset_id)
    )
