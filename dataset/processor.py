import logging

import simplejson as json

from dataset import meta_data_aggregator
from dataset.definitions import definitions
from pelican.util.services import get_cursor

logger = logging.getLogger("pelican.dataset.processor")


def do_work(dataset_id):
    check_scope = {}
    meta_data_aggregator_scope = {}

    with get_cursor(name="dataset") as named_cursor:
        named_cursor.execute(
            "SELECT id, data FROM data_item WHERE dataset_id = %(dataset_id)s",
            {"dataset_id": dataset_id},
        )

        for i, item in enumerate(named_cursor, 1):
            for check_name, check in definitions.items():
                check_scope.setdefault(check_name, {})
                check_scope[check_name] = check.add_item(check_scope[check_name], item["data"], item["id"])

            meta_data_aggregator_scope = meta_data_aggregator.add_item(
                meta_data_aggregator_scope, item["data"], item["id"]
            )

            if not i % 50000:  # about once per 15s
                logger.info("Processed %s data items", i)

    if "i" not in locals():
        logger.info("No item with dataset_id %s found. Skipping dataset checks computation.", dataset_id)
        return

    with get_cursor() as cursor:
        for check_name, check in definitions.items():
            logger.info("Getting result for %s dataset check.", check_name)
            result = check.get_result(check_scope[check_name])

            if "meta" not in result or result["meta"] is None:
                result["meta"] = {}

            result["meta"]["version"] = result["version"]
            meta = json.dumps(result["meta"])

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

    logger.info("Saving meta data for dataset_id %s", dataset_id)
    meta_data = meta_data_aggregator.get_result(meta_data_aggregator_scope)
    meta_data_aggregator.update_meta_data(meta_data, dataset_id)
