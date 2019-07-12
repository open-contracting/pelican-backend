import sys
import time

from dataset.definitions import definitions
from tools.db import commit, get_cursor

page_size = 1000


def do_work(dataset_id, logger):
    processed_count = 1000
    id = -1
    pager = 0
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
                plugin.add_item(item)

            processed_count = processed_count + 1
            id = item["id"]

        pager = pager + 1

        logger.info("Processed page {}".format(pager))

    for plugin_name, plugin in definitions.items():
        print(plugin.get_result())

    time.sleep(1)

    sys.exit()
    return
