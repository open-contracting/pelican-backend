import sys
import time
import simplejson as json

from contracting_process.field_level.definitions import \
    definitions as field_level_definitions, coverage_checks
from contracting_process.resource_level.definitions import \
    definitions as resource_level_definitions
from tools.db import commit, get_cursor
from tools.getter import get_values
from tools.logging_helper import get_logger


def do_work(data, item_id, dataset_id):
    field_level_checks(data, item_id, dataset_id)

    resource_level_checks(data, item_id, dataset_id)

    commit()

    return None


def resource_level_checks(data, item_id, dataset_id):
    # perform resource level checks
    for check_name, checks in resource_level_definitions.items():
        # confront value with its checks
        for check in checks:
            check_result = check(data)
            save_resource_level_check(check_name, check_result, item_id, dataset_id)


def field_level_checks(data, item_id, dataset_id):
    result = {}

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
            result[path] = []

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

                    result[path].append(field_result)

    # save result
    save_field_level_check(result, item_id, dataset_id)


def save_field_level_check(result, item_id, dataset_id):
    cursor = get_cursor()

    cursor.execute("""
        INSERT INTO field_level_check
        (result, data_item_id, dataset_id)
        VALUES
        (%s, %s, %s);
        """, (json.dumps(result), item_id, dataset_id)
    )


def save_resource_level_check(check_name, result, item_id, dataset_id):
    cursor = get_cursor()

    if "meta" not in result or not result["meta"]:
        result["meta"] = {}

    result["meta"]["version"] = result["version"]
    meta = json.dumps(result["meta"])

    cursor.execute("""
        INSERT INTO resource_level_check
        (check_name, result, pass_count, application_count, meta, data_item_id, dataset_id)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)
        """, (
        check_name,
        result["result"],
        result["pass_count"],
        result["application_count"],
        meta,
        item_id,
        dataset_id)
    )
