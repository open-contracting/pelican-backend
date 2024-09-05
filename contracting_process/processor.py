import logging

from psycopg2.extras import execute_values

from contracting_process.field_level.definitions import coverage_checks
from contracting_process.field_level.definitions import definitions as field_level_definitions
from contracting_process.resource_level.definitions import definitions as resource_level_definitions
from pelican.util import settings
from pelican.util.getter import get_values
from pelican.util.services import Json, State, get_cursor, update_items_state
from pelican.util.workers import is_step_required

logger = logging.getLogger("pelican.contracting_process.processor")


def do_work(dataset_id, items):
    field_level_check_arglist = []
    resource_level_check_arglist = []

    do_field_level = is_step_required(settings.Steps.FIELD_COVERAGE, settings.Steps.FIELD_QUALITY)
    do_resource_level = is_step_required(settings.Steps.COMPILED_RELEASE)
    do_field_quality = is_step_required(settings.Steps.FIELD_QUALITY)

    for data, item_id in items:
        if "ocid" not in data:
            logger.error("data_item %s has no ocid", item_id)
            continue
        if do_field_level:
            field_level_check_arglist.append(
                field_level_checks(data, item_id, dataset_id, do_field_quality=do_field_quality)
            )
        if do_resource_level:
            resource_level_check_arglist.append(resource_level_checks(data, item_id, dataset_id))

    update_items_state(dataset_id, (item_id for _, item_id in items), State.OK)

    if do_field_level:
        save_field_level_checks(field_level_check_arglist)
    if do_resource_level:
        save_resource_level_check(resource_level_check_arglist)


def resource_level_checks(data, item_id, dataset_id):
    logger.debug("Dataset %s: Item %s: Calculating compiled release-level checks", dataset_id, item_id)

    result = {"meta": {"ocid": data["ocid"], "item_id": item_id}, "checks": {}}

    for check_name, check in resource_level_definitions.items():
        result["checks"][check_name] = check(data)

    return (Json(result), item_id, dataset_id)


def field_level_checks(data, item_id, dataset_id, *, do_field_quality=True):
    logger.debug("Dataset %s: Item %s: Calculating field-level checks", dataset_id, item_id)

    result = {"meta": {"ocid": data["ocid"], "item_id": item_id}, "checks": {}}

    for path, checks in field_level_definitions.items():
        if "." in path:
            # dive deeper in tree
            ancestors, leaf = path.rsplit(".", 1)
            values = get_values(data, ancestors)
        else:
            # checking top level item
            leaf = path
            values = [{"path": "", "value": data}]

        if not values:
            continue

        result["checks"][path] = []

        # iterate over parents and perform checks
        for value in values:
            list_result = type(value["value"]) is list

            # create list from plain values
            if not list_result:
                value["value"] = [value["value"]]

            # iterate over all returned values and check those
            for i, item in enumerate(value["value"]):
                field_result = {
                    "coverage": {"overall_result": None, "check_results": []},
                    "quality": {"overall_result": None, "check_results": []},
                }

                # construct path based on "is the parent a list?"
                if list_result:
                    field_result["path"] = f"{value['path']}[{i}].{leaf}"
                elif value["path"]:
                    field_result["path"] = f"{value['path']}.{leaf}"
                else:
                    field_result["path"] = leaf

                for check, _ in coverage_checks:
                    check_result = check(item, leaf)
                    passed = check_result["result"]
                    field_result["coverage"]["check_results"].append(check_result)
                    field_result["coverage"]["overall_result"] = passed
                    if passed is False:
                        break
                else:  # field_result["coverage"]["overall_result"] is True
                    if do_field_quality:
                        for check, _ in checks:
                            check_result = check(item, leaf)
                            passed = check_result["result"]
                            field_result["quality"]["check_results"].append(check_result)
                            field_result["quality"]["overall_result"] = passed
                            if passed is False:
                                break

                result["checks"][path].append(field_result)

    return (Json(result), item_id, dataset_id)


def save_field_level_checks(arglist):
    with get_cursor() as cursor:
        sql = "INSERT INTO field_level_check (result, data_item_id, dataset_id) VALUES %s"
        execute_values(cursor, sql, arglist)


def save_resource_level_check(arglist):
    with get_cursor() as cursor:
        sql = "INSERT INTO resource_level_check (result, data_item_id, dataset_id) VALUES %s"
        execute_values(cursor, sql, arglist)
