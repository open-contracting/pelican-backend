import sys
import time

import simplejson as json

from dataset.definitions import definitions
import dataset.meta_data_aggregator as meta_data_aggregator
from tools.db import commit, get_cursor
from settings.settings import CustomLogLevels

page_size = 1000


def do_work(dataset_id, logger):
    processed_count = 1000
    id = -1
    no_item_processed = True
    pager = 0
    scope = {}
    meta_data_aggregator_scope = {}

    while processed_count == page_size:
        processed_count = 0
        cursor = get_cursor()

        cursor.execute("""
            SELECT * FROM data_item
            WHERE
                id > %s
                and dataset_id = %s
            ORDER BY ID
            LIMIT %s
        """, (id, dataset_id, page_size))

        items = cursor.fetchall()

        for item in items:
            for plugin_name, plugin in definitions.items():
                logger.log(CustomLogLevels.CHECK_TRACE, "Computing {} check for item_id {}.".format(plugin_name, item["id"]))

                if plugin_name not in scope:
                    scope[plugin_name] = {}

                try:
                    scope[plugin_name] = plugin.add_item(scope[plugin_name], item["data"], item["id"])
                except:
                    logger.error(
                        "Something went wrong when computing dataset level check: "
                        "check = {}, item_id = {}, dataset_id = {}."
                        "".format(plugin_name, item["id"], dataset_id)
                    )
                    raise

            processed_count = processed_count + 1
            id = item["id"]
            no_item_processed = False

            meta_data_aggregator_scope = meta_data_aggregator.add_item(
                meta_data_aggregator_scope, item["data"], item["id"]
            )

        pager = pager + 1

        logger.info("Processed page {}".format(pager))

    if no_item_processed:
        logger.info(
            "No item with dataset_id {} found. Skipping dataset checks computation.".format(dataset_id)
        )
        return

    for plugin_name, plugin in definitions.items():
        logger.info(
            "Getting result for {} dataset check.".format(plugin_name)
        )
        result = plugin.get_result(scope[plugin_name])
        save_dataset_level_check(plugin_name, result, dataset_id)

    logger.info("Saving meta data for dataset_id {}".format(dataset_id))
    meta_data = meta_data_aggregator.get_result(meta_data_aggregator_scope)
    meta_data_aggregator.update_meta_data(meta_data, dataset_id)

    return


def save_dataset_level_check(check_name, result, dataset_id):
    cursor = get_cursor()

    if "meta" not in result or result["meta"] is None:
        result["meta"] = {}

    result["meta"]["version"] = result["version"]
    meta = json.dumps(result["meta"])

    cursor.execute("""
        INSERT INTO dataset_level_check
        (check_name, result, value, meta, dataset_id)
        VALUES
        (%s, %s, %s, %s, %s)
        """, (
        check_name,
        result["result"],
        result["value"],
        meta,
        dataset_id)
    )
