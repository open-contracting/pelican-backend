import sys
import time

from psycopg2.extras import Json

from dataset.definitions import definitions
from tools.db import commit, get_cursor

page_size = 1000


def do_work(dataset_id, logger):
    processed_count = 1000
    id = -1
    pager = 0
    scope = {}

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

        pager = pager + 1

        logger.info("Processed page {}".format(pager))

    for plugin_name, plugin in definitions.items():
        result = plugin.get_result(scope[plugin_name])
        save_dataset_level_check(plugin_name, result, dataset_id)

    time.sleep(1)
    return


def save_dataset_level_check(check_name, result, dataset_id):
    cursor = get_cursor()

    result["meta"]["version"] = result["version"]
    meta = Json(result["meta"])

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
