import sys
import time
import simplejson as json
from psycopg2.extras import execute_values

from contracting_process.field_level.definitions import \
    definitions as field_level_definitions, coverage_checks
from contracting_process.resource_level.definitions import \
    definitions as resource_level_definitions
from tools.db import get_cursor
from tools.getter import get_values
from tools.logging_helper import get_logger
from core.state import set_item_state, state


# item: (data, item_id, dataset_id)
def do_work(items):
    field_level_check_results = []
    resource_level_check_results = []

    items_count = 0
    for item in items:
        items_count += 1

        field_level_check_results.append(field_level_checks(*item))

        resource_level_check_results.append(resource_level_checks(*item))

        set_item_state(item[2], item[1], state.OK)

    save_field_level_checks(field_level_check_results, items_count)
    save_resource_level_check(resource_level_check_results, items_count)

    return None


def resource_level_checks(data, item_id, dataset_id):
    result = {
        "meta": {
            "ocid": data["ocid"],
            "item_id": item_id
        },
        "checks": {

        }
    }

    # perform resource level checks
    for check_name, check in resource_level_definitions.items():
        result["checks"][check_name] = check(data)

    # return result
    return (json.dumps(result), item_id, dataset_id)


def field_level_checks(data, item_id, dataset_id):
    result = {
        "meta": {
            "ocid": data["ocid"],
            "item_id": item_id
        },
        "checks": {

        }
    }

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
            # adding path to result
            result["checks"][path] = []

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
                    field_result = {
                        "path": None,
                        "coverage": {
                            "overall_result": None,
                            "check_results": None
                        },
                        "quality": {
                            "overall_result": None,
                            "check_results": None
                        }
                    }

                    # construct path based on "is the parent a list?"
                    if list_result:
                        field_result["path"] = "{}[{}].{}".format(value["path"], counter, path_chunks[-1])
                    else:
                        if value["path"]:
                            field_result["path"] = "{}.{}".format(value["path"], path_chunks[-1])
                        else:
                            field_result["path"] = path_chunks[-1]

                    counter = counter + 1

                    # coverage checks
                    for check, _ in coverage_checks:
                        if field_result["coverage"]["check_results"] is None:
                            field_result["coverage"]["check_results"] = []

                        try:
                            check_result = check(item, path_chunks[-1])
                        except Exception:
                            get_logger().exception(
                                "Something went wrong when computing checks in path '{}'".format(path)
                            )
                            raise Exception

                        field_result["coverage"]["check_results"].append(check_result)
                        field_result["coverage"]["overall_result"] = check_result["result"]

                        if check_result["result"] is False:
                            break

                    # quality checks
                    if field_result["coverage"]["overall_result"]:
                        for check, _ in checks:
                            if field_result["quality"]["check_results"] is None:
                                field_result["quality"]["check_results"] = []

                            try:
                                check_result = check(item, path_chunks[-1])
                            except Exception:
                                get_logger().exception(
                                    "Something went wrong when computing checks in path '{}'".format(path)
                                )
                                raise Exception

                            field_result["quality"]["check_results"].append(check_result)
                            field_result["quality"]["overall_result"] = check_result["result"]

                            if check_result["result"] is False:
                                break

                    result["checks"][path].append(field_result)

    # return result
    return (json.dumps(result), item_id, dataset_id)


# result_item: (result, item_id, dataset_id)
def save_field_level_checks(result_items, items_count):
    cursor = get_cursor()

    sql = """
        INSERT INTO field_level_check
        (result, data_item_id, dataset_id)
        VALUES
        %s;
    """

    execute_values(cursor, sql, result_items, page_size=items_count)


# result_item: (result, item_id, dataset_id)
def save_resource_level_check(result_items, items_count):
    cursor = get_cursor()

    sql = """
        INSERT INTO resource_level_check
        (result, data_item_id, dataset_id)
        VALUES
        %s;
    """

    execute_values(cursor, sql, result_items, page_size=items_count)
