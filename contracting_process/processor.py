import logging

import simplejson as json
from psycopg2.extras import execute_values

from contracting_process.field_level.definitions import coverage_checks
from contracting_process.field_level.definitions import definitions as field_level_definitions
from contracting_process.resource_level.definitions import definitions as resource_level_definitions
from tools import settings
from tools.getter import get_values
from tools.services import get_cursor, state, update_items_state
from tools.workers import is_step_required

logger = logging.getLogger("pelican.contracting_process.processor")


# item: (data, item_id)
def do_work(dataset_id, items):
    field_level_check_results = []
    resource_level_check_results = []

    do_field_level = is_step_required(settings.Steps.FIELD_COVERAGE, settings.Steps.FIELD_QUALITY)
    do_resource_level = is_step_required(settings.Steps.COMPILED_RELEASE)
    do_field_quality = is_step_required(settings.Steps.FIELD_QUALITY)

    items_count = 0
    for item in items:
        items_count += 1

        if do_field_level:
            field_level_check_results.append(field_level_checks(*item, dataset_id, do_field_quality=do_field_quality))
        if do_resource_level:
            resource_level_check_results.append(resource_level_checks(*item, dataset_id))

    update_items_state(dataset_id, (item[1] for item in items), state.OK)

    if do_field_level:
        save_field_level_checks(field_level_check_results, items_count)
    if do_resource_level:
        save_resource_level_check(resource_level_check_results, items_count)


def resource_level_checks(data, item_id, dataset_id):
    logger.log(
        settings.CustomLogLevels.CHECK_TRACE,
        "Computing resource level checks for item_id = %s, dataset_id = %s.",
        item_id,
        dataset_id,
    )

    result = {"meta": {"ocid": data["ocid"], "item_id": item_id}, "checks": {}}

    # perform resource level checks
    for check_name, check in resource_level_definitions.items():
        logger.log(settings.CustomLogLevels.CHECK_TRACE, "Computing %s check.", check_name)
        result["checks"][check_name] = check(data)

    # return result
    return (json.dumps(result), item_id, dataset_id)


def field_level_checks(data, item_id, dataset_id, do_field_quality=True):
    logger.log(
        settings.CustomLogLevels.CHECK_TRACE,
        "Computing field level checks for item_id = %s, dataset_id = %s.",
        item_id,
        dataset_id,
    )

    result = {"meta": {"ocid": data["ocid"], "item_id": item_id}, "checks": {}}

    for path, checks in field_level_definitions.items():
        # get the parent/parents
        path_chunks = path.split(".")

        values = []
        if len(path_chunks) > 1:
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
                if type(value["value"]) is not list:
                    value["value"] = [value["value"]]
                    list_result = False

                # iterate over all returned values and check those
                counter = 0
                for item in value["value"]:
                    field_result = {
                        "path": None,
                        "coverage": {"overall_result": None, "check_results": None},
                        "quality": {"overall_result": None, "check_results": None},
                    }

                    # construct path based on "is the parent a list?"
                    if list_result:
                        field_result["path"] = f"{value['path']}[{counter}].{path_chunks[-1]}"
                    else:
                        if value["path"]:
                            field_result["path"] = f"{value['path']}.{path_chunks[-1]}"
                        else:
                            field_result["path"] = path_chunks[-1]

                    counter += 1

                    for check, check_name in coverage_checks:
                        logger.log(
                            settings.CustomLogLevels.CHECK_TRACE,
                            "Computing %s check in %s path.",
                            check_name,
                            path,
                        )

                        if field_result["coverage"]["check_results"] is None:
                            field_result["coverage"]["check_results"] = []

                        check_result = check(item, path_chunks[-1])
                        field_result["coverage"]["check_results"].append(check_result)
                        field_result["coverage"]["overall_result"] = check_result["result"]

                        if check_result["result"] is False:
                            break

                    if do_field_quality and field_result["coverage"]["overall_result"]:
                        for check, check_name in checks:
                            logger.log(
                                settings.CustomLogLevels.CHECK_TRACE,
                                "Computing %s check in %s path.",
                                check_name,
                                path,
                            )

                            if field_result["quality"]["check_results"] is None:
                                field_result["quality"]["check_results"] = []

                            check_result = check(item, path_chunks[-1])
                            field_result["quality"]["check_results"].append(check_result)
                            field_result["quality"]["overall_result"] = check_result["result"]

                            if check_result["result"] is False:
                                break

                    result["checks"][path].append(field_result)

    return (json.dumps(result), item_id, dataset_id)


def save_field_level_checks(result_items, items_count):
    with get_cursor() as cursor:
        sql = "INSERT INTO field_level_check (result, data_item_id, dataset_id) VALUES %s"
        execute_values(cursor, sql, result_items, page_size=items_count)

    logger.debug("Field level checks saved.")


def save_resource_level_check(result_items, items_count):
    with get_cursor() as cursor:
        sql = "INSERT INTO resource_level_check (result, data_item_id, dataset_id) VALUES %s"
        execute_values(cursor, sql, result_items, page_size=items_count)

    logger.debug("Resource level checks saved.")
