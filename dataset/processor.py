import logging

from dataset import metadata_aggregator
from dataset.definitions import definitions
from pelican.util.services import Json, get_cursor

logger = logging.getLogger("pelican.dataset.processor")


def do_work(dataset_id):
    check_scope = {}
    metadata_aggregator_scope = {}

    with get_cursor(name="dataset") as named_cursor:
        named_cursor.execute(
            "SELECT id, data FROM data_item WHERE dataset_id = %(dataset_id)s",
            {"dataset_id": dataset_id},
        )

        for i, item in enumerate(named_cursor, 1):
            for check_name, check in definitions.items():
                check_scope.setdefault(check_name, {})
                check_scope[check_name] = check.add_item(check_scope[check_name], item["data"], item["id"])

            metadata_aggregator_scope = metadata_aggregator.add_item(
                metadata_aggregator_scope, item["data"], item["id"]
            )

            if not i % 50000:  # about once per 15s
                logger.info("Dataset %s: Processed %s data items", dataset_id, i)

    if "i" not in locals():
        logger.info("Dataset %s: No items found, skipping dataset-level checks", dataset_id)
        return

    with get_cursor() as cursor:
        for check_name, check in definitions.items():
            logger.info("Dataset %s: Inserting %s dataset-level check result", dataset_id, check_name)
            result = check.get_result(check_scope[check_name])

            if "meta" not in result or result["meta"] is None:
                result["meta"] = {}

            result["meta"]["version"] = result["version"]

            cursor.execute(
                """\
                INSERT INTO dataset_level_check (check_name, result, value, meta, dataset_id)
                VALUES (%(check_name)s, %(result)s, %(value)s, %(meta)s, %(dataset_id)s)
                """,
                {
                    "check_name": check_name,
                    "result": result["result"],
                    "value": result["value"],
                    "meta": Json(result["meta"]),
                    "dataset_id": dataset_id,
                },
            )

    logger.info("Dataset %s: Updating with dataset metadata", dataset_id)
    metadata = metadata_aggregator.get_result(metadata_aggregator_scope)
    metadata_aggregator.update_metadata(metadata, dataset_id)
