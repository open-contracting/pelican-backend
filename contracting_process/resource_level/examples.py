import simplejson as json

from contracting_process.resource_level.definitions import definitions
from tools.helpers import ReservoirSampler
from tools.services import commit, get_cursor

examples_cap = 20


def create(dataset_id):
    cursor = get_cursor()

    # Delete existing data in case of duplicate messages.
    cursor.execute(
        "DELETE FROM resource_level_check_examples WHERE dataset_id = %(dataset_id)s", {"dataset_id": dataset_id}
    )

    check_samplers = {
        check_name: {
            "passed": ReservoirSampler(examples_cap),
            "failed": ReservoirSampler(examples_cap),
            "undefined": ReservoirSampler(examples_cap),
        }
        for check_name in definitions
    }

    cursor.execute(
        """\
        SELECT result->'meta' AS meta, d.value AS result, d.key AS check_name
        FROM resource_level_check, jsonb_each(result->'checks') d
        WHERE dataset_id = %(dataset_id)s
        """,
        {"dataset_id": dataset_id},
    )

    while True:
        row = cursor.fetchone()
        if row is None:
            break

        example = {"meta": row[0], "result": row[1]}

        if example["result"]["result"] is True:
            check_samplers[row[2]]["passed"].process(example)
        elif example["result"]["result"] is False:
            check_samplers[row[2]]["failed"].process(example)
        elif example["result"]["result"] is None:
            check_samplers[row[2]]["undefined"].process(example)
        else:
            raise ValueError

    for check_name, samplers in check_samplers.items():
        data = {
            "passed_examples": samplers["passed"].retrieve_samples(),
            "failed_examples": samplers["failed"].retrieve_samples(),
            "undefined_examples": samplers["undefined"].retrieve_samples(),
        }

        cursor.execute(
            """\
            INSERT INTO resource_level_check_examples (dataset_id, check_name, data)
            VALUES (%(dataset_id)s, %(check_name)s, %(data)s)
            """,
            {"dataset_id": dataset_id, "check_name": check_name, "data": json.dumps(data)},
        )

    commit()

    cursor.close()
