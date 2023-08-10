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
    cursor.execute(
        """\
        DELETE FROM report WHERE dataset_id = %(dataset_id)s AND type = 'field_level_check';
        DELETE FROM field_level_check_examples WHERE dataset_id = %(dataset_id)s;
        """,
        {"dataset_id": dataset_id},
    )

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
                "passed_examples": [],
                "failed_examples": [],
                "passed_sampler": ReservoirSampler(sample_size),
                "failed_sampler": ReservoirSampler(sample_size),
            }

            for _, check_name in checks:
                report[path][key]["checks"][check_name] = {
                    "passed_count": 0,
                    "failed_count": 0,
                    "total_count": 0,
                }

                examples[path][key]["checks"][check_name] = {
                    "passed_examples": [],
                    "failed_examples": [],
                    "passed_sampler": ReservoirSampler(sample_size),
                    "failed_sampler": ReservoirSampler(sample_size),
                }

    logger.info("Starting processing pages.")

    with get_cursor(name="field_level_report_examples") as named_cursor:
        named_cursor.execute(
            "SELECT result FROM field_level_check WHERE dataset_id = %(dataset_id)s",
            {"dataset_id": dataset_id},
        )

        for i, row in enumerate(named_cursor, 1):
            result = row["result"]
            meta = result["meta"]

            for path, path_checks in result["checks"].items():
                for path_check in path_checks:
                    exact_path = path_check["path"]

                    for key in ("coverage", "quality"):
                        if path_check[key]["overall_result"]:
                            report[path][key]["passed_count"] += 1
                        else:
                            report[path][key]["failed_count"] += 1

                        report[path][key]["total_count"] += 1

                        for check in path_check[key]["check_results"]:
                            example = {"meta": meta, "path": exact_path, "result": check}

                            prefix = "passed" if check["result"] else "failed"
                            report[path][key]["checks"][check["name"]][f"{prefix}_count"] += 1
                            examples[path][key]["checks"][check["name"]][f"{prefix}_sampler"].process(example)
                            examples[path][key][f"{prefix}_sampler"].process(example)

                            report[path][key]["checks"][check["name"]]["total_count"] += 1

                        if not path_check["coverage"]["overall_result"] or not path_check["quality"]["check_results"]:
                            break

            if i % 1000:
                logger.info("Processed %s field-level check results", i)

    logger.info("Storing field level check report for dataset_id %s", dataset_id)
    cursor.execute(
        "INSERT INTO report (dataset_id, type, data) VALUES (%(dataset_id)s, 'field_level_check', %(data)s)",
        {"dataset_id": dataset_id, "data": json.dumps(report)},
    )

    commit()

    logger.info("Storing examples for field level checks for dataset_id %s", dataset_id)
    for path, path_checks in examples.items():
        for key in ("coverage", "quality"):
            path_checks[key]["passed_examples"] = path_checks[key]["passed_sampler"].sample
            path_checks[key]["failed_examples"] = path_checks[key]["failed_sampler"].sample

            del path_checks[key]["passed_sampler"]
            del path_checks[key]["failed_sampler"]

            for check_name, check in path_checks[key]["checks"].items():
                check["passed_examples"] = check["passed_sampler"].sample
                check["failed_examples"] = check["failed_sampler"].sample

                del check["passed_sampler"]
                del check["failed_sampler"]

        cursor.execute(
            """\
            INSERT INTO field_level_check_examples (dataset_id, path, data)
            VALUES (%(dataset_id)s, %(path)s, %(data)s)
            """,
            {"dataset_id": dataset_id, "path": path, "data": json.dumps(path_checks)},
        )

    commit()

    cursor.close()
