import logging

from pelican.util.checks import get_empty_result_time_based, get_empty_result_time_based_scope
from pelican.util.services import Json, get_cursor
from time_variance.definitions import definitions

logger = logging.getLogger("pelican.time_variance.processor")


def do_work(dataset_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM dataset WHERE id = %(id)s", {"id": dataset_id})
        ancestor_id = cursor.fetchone()["ancestor_id"]

    if not ancestor_id:
        logger.info("Dataset %s: No ancestor available, skipping time-based checks", dataset_id)
        return

    with get_cursor() as cursor:
        cursor.execute("ANALYZE data_item")

    scope = {}

    with get_cursor(name="time_based") as named_cursor:
        named_cursor.execute(
            """\
            SELECT ancestor_data_item.id, ancestor_data_item.data, new_data_item.id, new_data_item.data
            FROM data_item ancestor_data_item
            LEFT JOIN data_item new_data_item ON
                ancestor_data_item.data->>'ocid' = new_data_item.data->>'ocid'
                AND new_data_item.dataset_id = %(dataset_id)s
            WHERE
                ancestor_data_item.dataset_id = %(ancestor_id)s
        """,
            {"dataset_id": dataset_id, "ancestor_id": ancestor_id},
        )

        for i, item in enumerate(named_cursor, 1):
            ancestor_item_id = item[0]
            ancestor_item = item[1]
            new_item_id = item[2]
            new_item = item[3]

            for check_name, check in definitions.items():
                scope.setdefault(check_name, get_empty_result_time_based_scope())

                if check.applicable(scope[check_name], ancestor_item, ancestor_item_id, new_item, new_item_id):
                    scope[check_name]["total_count"] += 1

                    # Time-based checks report two numbers: "pairs found" and "pairs passed" (as a percentage of
                    # pairs found). This if-statement serves to calculate the "pairs found".
                    #
                    # In general, time-based checks require the new item to be present in order to be evaluated,
                    # which this if-statement guarantees. The `ocid` check is special, because its "pairs passed"
                    # test is the same as this "pairs found" test. As such, its "pairs passed" result will always
                    # be 100%. In short: this if-statement is not in error.
                    if new_item_id:
                        scope[check_name]["coverage_count"] += 1
                        scope[check_name], evaluation_result = check.evaluate(
                            scope[check_name], ancestor_item, ancestor_item_id, new_item, new_item_id
                        )

                        if evaluation_result:
                            scope[check_name]["ok_count"] += 1
                        else:
                            scope[check_name]["failed_count"] += 1
                            scope[check_name]["examples"].process(
                                {
                                    "item_id": ancestor_item_id,
                                    "new_item_id": new_item_id,
                                    "ocid": ancestor_item["ocid"],
                                    "new_item_ocid": new_item["ocid"],
                                }
                            )

            if not i % 1000:
                logger.info("Dataset %s: Processed %s data items", dataset_id, i)

    if "i" not in locals():
        logger.info("Dataset %s: No items found, skipping time-based checks", dataset_id)
        return

    with get_cursor() as cursor:
        for check_name, check in definitions.items():
            logger.info("Dataset %s: Inserting %s time-based check result", dataset_id, check_name)
            result = get_result(scope[check_name], check.version)

            if "meta" not in result or result["meta"] is None:
                result["meta"] = {}

            result["meta"]["version"] = result["version"]
            result["meta"]["examples"] = result["examples"]

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
                    "meta": Json(result["meta"]),
                },
            )


def get_result(scope, version):
    result = get_empty_result_time_based(version)

    if scope["coverage_count"] > 0:
        result["check_value"] = round(scope["ok_count"] / (scope["coverage_count"] / 100))
        result["check_result"] = result["check_value"] > 95

    if scope["total_count"] > 0:
        result["coverage_value"] = round(scope["coverage_count"] / (scope["total_count"] / 100))
        result["coverage_result"] = result["coverage_value"] > 95

    result["examples"] = scope["examples"].sample

    result["meta"] = {
        "total_count": scope["total_count"],
        "coverage_count": scope["coverage_count"],
        "failed_count": scope["failed_count"],
        "ok_count": scope["ok_count"],
    }

    return result
