import simplejson as json

from dataset import meta_data_aggregator
from dataset.definitions import definitions
from pelican.util import settings
from pelican.util.services import get_cursor

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

        cursor.execute(
            "SELECT * FROM data_item WHERE id > %(id)s AND dataset_id = %(dataset_id)s ORDER BY id LIMIT %(limit)s",
            {"id": id, "dataset_id": dataset_id, "limit": page_size},
        )

        items = cursor.fetchall()

        for item in items:
            for plugin_name, plugin in definitions.items():
                logger.log(
                    settings.CustomLogLevels.CHECK_TRACE,
                    "Computing %s check for item_id %s.",
                    plugin_name,
                    item["id"],
                )

                if plugin_name not in scope:
                    scope[plugin_name] = {}

                scope[plugin_name] = plugin.add_item(scope[plugin_name], item["data"], item["id"])

            processed_count += 1
            id = item["id"]
            no_item_processed = False

            meta_data_aggregator_scope = meta_data_aggregator.add_item(
                meta_data_aggregator_scope, item["data"], item["id"]
            )

        pager += 1

        logger.info("Processed page %s", pager)

        cursor.close()

    if no_item_processed:
        logger.info("No item with dataset_id %s found. Skipping dataset checks computation.", dataset_id)
        return

    for plugin_name, plugin in definitions.items():
        logger.info("Getting result for %s dataset check.", plugin_name)
        result = plugin.get_result(scope[plugin_name])
        save_dataset_level_check(plugin_name, result, dataset_id)

    logger.info("Saving meta data for dataset_id %s", dataset_id)
    meta_data = meta_data_aggregator.get_result(meta_data_aggregator_scope)
    meta_data_aggregator.update_meta_data(meta_data, dataset_id)


def save_dataset_level_check(check_name, result, dataset_id):
    if "meta" not in result or result["meta"] is None:
        result["meta"] = {}

    result["meta"]["version"] = result["version"]
    meta = json.dumps(result["meta"])

    with get_cursor() as cursor:
        cursor.execute(
            """\
            INSERT INTO dataset_level_check (check_name, result, value, meta, dataset_id)
            VALUES (%(check_name)s, %(result)s, %(value)s, %(meta)s, %(dataset_id)s)
            """,
            {
                "check_name": check_name,
                "result": result["result"],
                "value": result["value"],
                "meta": meta,
                "dataset_id": dataset_id,
            },
        )
