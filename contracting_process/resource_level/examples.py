import simplejson as json

from contracting_process.resource_level.definitions import definitions
from tools.db import commit, get_cursor
from tools.helpers import ReservoirSampler

examples_cap = 20


def create(dataset_id):
    cursor = get_cursor()
    cursor.execute(
        """
        delete
        from resource_level_check_examples
        where dataset_id = %s;
        """,
        [dataset_id],
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
        """
        select result->'meta' as meta, d.value as result, d.key as check_name
        from resource_level_check, jsonb_each(result->'checks') d
        where dataset_id = %s;
        """,
        [dataset_id],
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
            raise ValueError()

    # saving examples
    for check_name, samplers in check_samplers.items():
        data = {
            "passed_examples": samplers["passed"].retrieve_samples(),
            "failed_examples": samplers["failed"].retrieve_samples(),
            "undefined_examples": samplers["undefined"].retrieve_samples(),
        }

        cursor.execute(
            """
            insert into resource_level_check_examples
            (dataset_id, check_name, data)
            values
            (%s, %s, %s);
            """,
            [dataset_id, check_name, json.dumps(data)],
        )
    commit()

    cursor.close()
