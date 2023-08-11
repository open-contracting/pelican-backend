import logging

from contracting_process.resource_level.definitions import definitions
from pelican.util.checks import ReservoirSampler
from pelican.util.services import Json, commit, get_cursor

logger = logging.getLogger("pelican.contracting_process.resource_level.examples")

sample_size = 20


def create(dataset_id):
    with get_cursor() as cursor:
        # Delete existing data in case of duplicate messages.
        cursor.execute(
            "DELETE FROM resource_level_check_examples WHERE dataset_id = %(dataset_id)s", {"dataset_id": dataset_id}
        )

    check_samplers = {
        check_name: {
            "passed": ReservoirSampler(sample_size),
            "failed": ReservoirSampler(sample_size),
            "undefined": ReservoirSampler(sample_size),
        }
        for check_name in definitions
    }

    with get_cursor(name="resource_level_examples") as named_cursor:
        named_cursor.execute(
            """\
            SELECT result
            FROM resource_level_check
            WHERE dataset_id = %(dataset_id)s
            """,
            {"dataset_id": dataset_id},
        )

        for i, row in enumerate(named_cursor, 1):
            value = row["result"]
            meta = value["meta"]
            for check_name, result in value["checks"].items():
                example = {"meta": meta, "result": result}
                passed = result["result"]

                if passed is True:
                    check_samplers[check_name]["passed"].process(example)
                elif passed is False:
                    check_samplers[check_name]["failed"].process(example)
                elif passed is None:
                    check_samplers[check_name]["undefined"].process(example)
                else:
                    raise NotImplementedError("result is not a boolean or null")

            if not i % 100000:  # about once per 10s
                logger.info("Dataset %s: Processed %s compiled release-level check results", dataset_id, i)

    with get_cursor() as cursor:
        for check_name, samplers in check_samplers.items():
            data = {
                "passed_examples": samplers["passed"].sample,
                "failed_examples": samplers["failed"].sample,
                "undefined_examples": samplers["undefined"].sample,
            }

            cursor.execute(
                """\
                INSERT INTO resource_level_check_examples (dataset_id, check_name, data)
                VALUES (%(dataset_id)s, %(check_name)s, %(data)s)
                """,
                {"dataset_id": dataset_id, "check_name": check_name, "data": Json(data)},
            )

    commit()
