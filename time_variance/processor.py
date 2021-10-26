import random

import simplejson as json

from time_variance.definitions import definitions
from tools.checks import get_empty_result_time_variance, get_empty_result_time_variance_scope
from tools.db import get_cursor
from tools.logging_helper import get_logger
from tools.settings import CustomLogLevels

page_size = 1000
examples_count = 50


def do_work(dataset_id):
    logger = get_logger()
    processed_count = 1000
    id = -1
    no_item_processed = True
    pager = 0
    scope = {}

    cursor = get_cursor()
    ancestor_id = get_ancestor_id(dataset_id, cursor)

    cursor.execute("ANALYZE data_item")

    if not ancestor_id:
        logger.info("No ancestor dataset available. Skipping time variance checks.")
        return

    while processed_count == page_size:
        processed_count = 0

        cursor.execute(
            """
            SELECT
                ancestor_data_item.id,
                ancestor_data_item.data,
                new_data_item.id,
                new_data_item.data
            FROM
                data_item ancestor_data_item
            LEFT JOIN
                data_item new_data_item
                ON
                    ancestor_data_item.data->>'ocid' = new_data_item.data->>'ocid'
                    AND new_data_item.dataset_id = %s
            WHERE
                ancestor_data_item.dataset_id = %s
                AND ancestor_data_item.id > %s
            ORDER BY
                ancestor_data_item.id
            LIMIT %s;
        """,
            (dataset_id, ancestor_id, id, page_size),
        )

        items = cursor.fetchall()

        for item in items:
            ancestor_item = item[1]
            ancestor_item_id = item[0]
            new_item = item[3]
            new_item_id = item[2]

            for plugin_name, plugin in definitions.items():
                logger.log(
                    CustomLogLevels.CHECK_TRACE, "Computing {} check for item_id {}.".format(plugin_name, item[0])
                )

                if plugin_name not in scope:
                    scope[plugin_name] = get_empty_result_time_variance_scope()

                try:
                    filtering_result = plugin.filter(
                        scope[plugin_name], ancestor_item, ancestor_item_id, new_item, new_item_id
                    )
                    if filtering_result:
                        scope[plugin_name]["total_count"] += 1

                        # Time-based checks report two numbers: "pairs found" and "pairs passed" (as a percentage of
                        # pairs found). This if-statement serves to calculate the "pairs found".
                        #
                        # In general, time-based checks require the new item to be present in order to be evaluated,
                        # which this if-statement guarantees. The `ocid` check is special, because its "pairs passed"
                        # test is the same as this "pairs found" test. As such, its "pairs passed" result will always
                        # be 100%. In short: this if-statement is not in error.
                        if item[2]:
                            scope[plugin_name]["coverage_count"] += 1
                            scope[plugin_name], evaluation_result = plugin.evaluate(
                                scope[plugin_name], ancestor_item, ancestor_item_id, new_item, new_item_id
                            )

                            if evaluation_result:
                                scope[plugin_name]["ok_count"] += 1
                            else:
                                scope[plugin_name]["failed_count"] += 1

                                if len(scope[plugin_name]["examples"]) < examples_count:
                                    scope[plugin_name]["examples"].append(
                                        {
                                            "item_id": ancestor_item_id,
                                            "new_item_id": new_item_id,
                                            "ocid": ancestor_item["ocid"],
                                            "new_item_ocid": new_item["ocid"],
                                        }
                                    )
                                else:
                                    rand_int = random.randint(0, scope[plugin_name]["failed_count"])
                                    if rand_int < examples_count:
                                        scope[plugin_name]["examples"][rand_int] = {
                                            "item_id": ancestor_item_id,
                                            "new_item_id": new_item_id,
                                            "ocid": ancestor_item["ocid"],
                                            "new_item_ocid": new_item["ocid"],
                                        }

                except Exception:
                    logger.error(
                        "Something went wrong when computing time variance level check: "
                        "check = {}, item_id = {}, dataset_id = {}."
                        "".format(plugin_name, ancestor_item_id, dataset_id)
                    )
                    raise

            processed_count = processed_count + 1
            id = item[0]
            no_item_processed = False

        pager = pager + 1

        logger.info("Processed page {}".format(pager))

    if no_item_processed:
        logger.info("No item with dataset_id {} found. Skipping time variance checks computation.".format(dataset_id))

    for plugin_name, plugin in definitions.items():
        logger.info("Getting result for {} time variance check.".format(plugin_name))
        result = get_result(scope[plugin_name], plugin.version)
        save_time_variance_level_check(plugin_name, result, dataset_id)

    cursor.close()


def save_time_variance_level_check(check_name, result, dataset_id):
    cursor = get_cursor()

    if "meta" not in result or result["meta"] is None:
        result["meta"] = {}

    result["meta"]["version"] = result["version"]
    result["meta"]["examples"] = result["examples"]
    meta = json.dumps(result["meta"])

    cursor.execute(
        """
        INSERT INTO time_variance_level_check
        (check_name, coverage_result, coverage_value, check_result, check_value, dataset_id, meta)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            check_name,
            result["coverage_result"],
            result["coverage_value"],
            result["check_result"],
            result["check_value"],
            dataset_id,
            meta,
        ),
    )


def get_ancestor_id(dataset_id, cursor):
    cursor.execute(
        """
            SELECT * FROM dataset
            WHERE id = %s
        """,
        (dataset_id,),
    )

    dataset = cursor.fetchone()

    return dataset["ancestor_id"]


def get_result(scope, version):
    result = get_empty_result_time_variance(version)

    if scope["coverage_count"] > 0:
        result["check_value"] = round(scope["ok_count"] / (scope["coverage_count"] / 100))
        result["check_result"] = result["check_value"] > 95

    if scope["total_count"] > 0:
        result["coverage_value"] = round(scope["coverage_count"] / (scope["total_count"] / 100))
        result["coverage_result"] = result["coverage_value"] > 95

    result["examples"] = scope["examples"]

    result["meta"] = {
        "total_count": scope["total_count"],
        "coverage_count": scope["coverage_count"],
        "failed_count": scope["failed_count"],
        "ok_count": scope["ok_count"],
    }

    return result
