import simplejson as json

from contracting_process.resource_level.definitions import definitions
from pelican.util.checks import ReservoirSampler
from pelican.util.services import commit, get_cursor

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
            SELECT result->'meta' AS meta, d.value AS result, d.key AS check_name
            FROM resource_level_check, jsonb_each(result->'checks') d
            WHERE dataset_id = %(dataset_id)s
            """,
            {"dataset_id": dataset_id},
        )

        for row in named_cursor:
            example = {"meta": row[0], "result": row[1]}

            if example["result"]["result"] is True:
                check_samplers[row[2]]["passed"].process(example)
            elif example["result"]["result"] is False:
                check_samplers[row[2]]["failed"].process(example)
            elif example["result"]["result"] is None:
                check_samplers[row[2]]["undefined"].process(example)
            else:
                raise ValueError

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
                {"dataset_id": dataset_id, "check_name": check_name, "data": json.dumps(data)},
            )

    commit()
