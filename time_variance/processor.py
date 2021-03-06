import logging
import random

import simplejson as json

from time_variance.definitions import definitions
from tools import settings
from tools.checks import get_empty_result_time_variance, get_empty_result_time_variance_scope
from tools.services import get_cursor

logger = logging.getLogger("pelican.time_variance.processor")

page_size = 1000
examples_count = 50


def do_work(dataset_id):
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
            """\
            SELECT ancestor_data_item.id, ancestor_data_item.data, new_data_item.id, new_data_item.data
            FROM data_item ancestor_data_item
            LEFT JOIN data_item new_data_item ON
                ancestor_data_item.data->>'ocid' = new_data_item.data->>'ocid'
                AND new_data_item.dataset_id = %(dataset_id)s
            WHERE
                ancestor_data_item.dataset_id = %(ancestor_id)s
                AND ancestor_data_item.id > %(id)s
            ORDER BY ancestor_data_item.id
            LIMIT %(limit)s
        """,
            {"dataset_id": dataset_id, "ancestor_id": ancestor_id, "id": id, "limit": page_size},
        )

        items = cursor.fetchall()

        for item in items:
            ancestor_item = item[1]
            ancestor_item_id = item[0]
            new_item = item[3]
            new_item_id = item[2]

            for plugin_name, plugin in definitions.items():
                logger.log(
                    settings.CustomLogLevels.CHECK_TRACE,
                    "Computing %s check for item_id %s.",
                    plugin_name,
                    item[0],
                )

                if plugin_name not in scope:
                    scope[plugin_name] = get_empty_result_time_variance_scope()

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

            processed_count += 1
            id = item[0]
            no_item_processed = False

        pager += 1

        logger.info("Processed page %s", pager)

    if no_item_processed:
        logger.info("No item with dataset_id %s found. Skipping time variance checks computation.", dataset_id)

    for plugin_name, plugin in definitions.items():
        logger.info("Getting result for %s time variance check.", plugin_name)
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
        """\
        INSERT INTO time_variance_level_check
        (check_name, coverage_result, coverage_value, check_result, check_value, dataset_id, meta)
        VALUES (
            %(check_name)s,
            %(coverage_result)s,
            %(coverage_value)s,
            %(check_result)s,
            %(check_value)s,
            %(dataset_id)s,
            %(meta)s
        )
        """,
        {
            "check_name": check_name,
            "coverage_result": result["coverage_result"],
            "coverage_value": result["coverage_value"],
            "check_result": result["check_result"],
            "check_value": result["check_value"],
            "dataset_id": dataset_id,
            "meta": meta,
        },
    )


def get_ancestor_id(dataset_id, cursor):
    cursor.execute("SELECT * FROM dataset WHERE id = %(id)s", {"id": dataset_id})
    return cursor.fetchone()["ancestor_id"]


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
