import sys
import time

import simplejson as json

from dataset.definitions import definitions
import dataset.meta_data_aggregator as meta_data_aggregator
from tools.db import commit, get_cursor

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
                if plugin_name not in scope:
                    scope[plugin_name] = {}
                scope[plugin_name] = plugin.add_item(scope[plugin_name], item["data"], item["id"])

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
    meta_data = meta_data_aggregator.get_meta_data(meta_data_aggregator_scope)
    cursor = get_cursor()
    cursor.execute(
        """
        UPDATE dataset
        SET meta = meta || %s
        WHERE id = %s;
        """, (json.dumps(meta_data), dataset_id)
    )

    return


def save_dataset_level_check(check_name, result, dataset_id):
    cursor = get_cursor()

    if "meta" not in result or result["meta"] is None:
        result["meta"] = {}

    result["meta"]["version"] = result["version"]
    meta = json.dumps(result["meta"])

    cursor.execute("""
        INSERT INTO dataset_level_check
        (check_name, result, value, meta, dataset_id, created, modified)
        VALUES
        (%s, %s, %s, %s, %s, now(), now())
        """, (
        check_name,
        result["result"],
        result["value"],
        meta,
        dataset_id)
    )
