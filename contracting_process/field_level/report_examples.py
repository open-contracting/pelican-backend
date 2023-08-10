import logging

import simplejson as json

from contracting_process.field_level.definitions import coverage_checks, definitions
from pelican.util.checks import ReservoirSampler
from pelican.util.services import commit, get_cursor

logger = logging.getLogger("pelican.contracting_process.field_level.report_examples")

sample_size = 20


def create(dataset_id):
    cursor = get_cursor()

    # Delete existing data in case of duplicate messages.
    parameters = {"dataset_id": dataset_id}
    cursor.execute("DELETE FROM report WHERE dataset_id = %(dataset_id)s AND type = 'field_level_check'", parameters)
    cursor.execute("DELETE FROM field_level_check_examples WHERE dataset_id = %(dataset_id)s", parameters)

    report = {}
    examples = {}

    for order, (path, quality_checks) in enumerate(definitions.items()):
        report[path] = {
            "examples_filled": False,
            "processing_order": order,
        }
        examples[path] = {}

        for key, checks in (("coverage", coverage_checks), ("quality", quality_checks)):
            report[path][key] = {
                "checks": {},
                "passed_count": 0,
                "failed_count": 0,
                "total_count": 0,
            }

            examples[path][key] = {
                "checks": {},
                "passed_examples": ReservoirSampler(sample_size),
                "failed_examples": ReservoirSampler(sample_size),
            }

            for _, check_name in checks:
                report[path][key]["checks"][check_name] = {
                    "passed_count": 0,
                    "failed_count": 0,
                    "total_count": 0,
                }

                examples[path][key]["checks"][check_name] = {
                    "passed_examples": ReservoirSampler(sample_size),
                    "failed_examples": ReservoirSampler(sample_size),
                }

    logger.info("Starting processing pages.")

    with get_cursor(name="field_level_report_examples") as named_cursor:
        named_cursor.execute(
            "SELECT result FROM field_level_check WHERE dataset_id = %(dataset_id)s",
            {"dataset_id": dataset_id},
        )

        for i, row in enumerate(named_cursor, 1):
            value = row["result"]
            meta = value["meta"]
            for path, entries in value["checks"].items():
                # If the path is to an array, the value corresponds to its entries.
                for entry in entries:
                    path_with_indexes = entry["path"]

                    for key in ("coverage", "quality"):
                        check_group = entry[key]
                        report_item = report[path][key]
                        examples_item = examples[path][key]

                        if check_group["overall_result"]:
                            report_item["passed_count"] += 1
                        else:
                            report_item["failed_count"] += 1
                        report_item["total_count"] += 1

                        for result in check_group["check_results"]:
                            example = {"meta": meta, "path": path_with_indexes, "result": result}
                            check_name = result["name"]

                            if result["result"]:
                                report_item["checks"][check_name]["passed_count"] += 1
                                examples_item["checks"][check_name]["passed_examples"].process(example)
                                examples_item["passed_examples"].process(example)
                            else:
                                report_item["checks"][check_name]["failed_count"] += 1
                                examples_item["checks"][check_name]["failed_examples"].process(example)
                                examples_item["failed_examples"].process(example)
                            report_item["checks"][check_name]["total_count"] += 1

                        # Skip the "quality" iteration if not covered or if no quality results.
                        if not entry["coverage"]["overall_result"] or not entry["quality"]["check_results"]:
                            break

            if not i % 5000:  # about once per 15s
                logger.info("Processed %s field-level check results", i)

    logger.info("Storing field level check report for dataset_id %s", dataset_id)
    cursor.execute(
        "INSERT INTO report (dataset_id, type, data) VALUES (%(dataset_id)s, 'field_level_check', %(data)s)",
        {"dataset_id": dataset_id, "data": json.dumps(report)},
    )

    commit()

    logger.info("Storing examples for field level checks for dataset_id %s", dataset_id)
    for path, check_groups in examples.items():
        for key in ("coverage", "quality"):
            check_group = check_groups[key]
            check_group["passed_examples"] = check_group["passed_examples"].sample
            check_group["failed_examples"] = check_group["failed_examples"].sample

            for check_name, check in check_group["checks"].items():
                check["passed_examples"] = check["passed_examples"].sample
                check["failed_examples"] = check["failed_examples"].sample

        cursor.execute(
            """\
            INSERT INTO field_level_check_examples (dataset_id, path, data)
            VALUES (%(dataset_id)s, %(path)s, %(data)s)
            """,
            {"dataset_id": dataset_id, "path": path, "data": json.dumps(checks)},
        )

    commit()

    cursor.close()
