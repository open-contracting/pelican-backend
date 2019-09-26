
import simplejson as json

from tools.db import commit
from tools.db import get_cursor
from tools.helpers import ReservoirSampler
from contracting_process.field_level.definitions import coverage_checks, definitions

examples_cap = 20


def create(dataset_id):
    cursor = get_cursor()
    cursor.execute(
        """
        delete
        from field_level_check_examples
        where dataset_id = '{}';
        """.format(dataset_id)
    )

    path_samplers = {}

    for path, quality_checks in definitions.items():

        path_samplers[path] = {
            'coverage': {
                'checks': {},
                'passed': ReservoirSampler(examples_cap),
                'failed': ReservoirSampler(examples_cap)
            },
            'quality': {
                'checks': {},
                'passed': ReservoirSampler(examples_cap),
                'failed': ReservoirSampler(examples_cap)
            }
        }

        for _, check_name in coverage_checks:
            path_samplers[path]['coverage']['checks'][check_name] = {
                'passed': ReservoirSampler(examples_cap),
                'failed': ReservoirSampler(examples_cap)
            }

        for _, check_name in quality_checks:
            path_samplers[path]['quality']['checks'][check_name] = {
                'passed': ReservoirSampler(examples_cap),
                'failed': ReservoirSampler(examples_cap)
            }

    # coverage
    cursor.execute(
        """
        select sub1.meta, sub1.exact_path, sub1.check, sub1.path
        from (
            select sub2.meta,
                   sub2.path,
                   sub2.path_check->>'path' as exact_path,
                   jsonb_array_elements(sub2.path_check->'coverage'->'check_results') as check
            from (
                select result->'meta' as meta, d.key as path, jsonb_array_elements(d.value) as path_check
                from field_level_check, jsonb_each(result->'checks') d
                where dataset_id = %s
            ) as sub2
            where sub2.path_check->'coverage'->>'check_results' is not null
        ) as sub1;
        """, [dataset_id]
    )

    while True:
        row = cursor.fetchone()
        if row is None:
            break

        example = {
            "meta": row[0],
            "path": row[1],
            "result": row[2]
        }

        if example["result"]["result"]:
            path_samplers[row[3]]['coverage']['passed'].process(example)
            path_samplers[row[3]]['coverage']['checks'][example['result']['name']]['passed'].process(example)
        else:
            path_samplers[row[3]]['coverage']['failed'].process(example)
            path_samplers[row[3]]['coverage']['checks'][example['result']['name']]['failed'].process(example)

    # quality
    cursor.execute(
        """
        select sub1.meta, sub1.exact_path, sub1.check, sub1.path
        from (
            select sub2.meta,
                   sub2.path,
                   sub2.path_check->>'path' as exact_path,
                   jsonb_array_elements(sub2.path_check->'quality'->'check_results') as check
            from (
                select result->'meta' as meta, d.key as path, jsonb_array_elements(d.value) as path_check
                from field_level_check, jsonb_each(result->'checks') d
                where dataset_id = %s
            ) as sub2
            where sub2.path_check->'quality'->>'check_results' is not null
        ) as sub1;
        """, [dataset_id]
    )

    while True:
        row = cursor.fetchone()
        if row is None:
            break

        example = {
            "meta": row[0],
            "path": row[1],
            "result": row[2]
        }

        if example["result"]["result"]:
            path_samplers[row[3]]['quality']['passed'].process(example)
            path_samplers[row[3]]['quality']['checks'][example['result']['name']]['passed'].process(example)
        else:
            path_samplers[row[3]]['quality']['failed'].process(example)
            path_samplers[row[3]]['quality']['checks'][example['result']['name']]['failed'].process(example)

    # saving examples
    for path, path_checks in path_samplers.items():

        path_checks['coverage']['passed_examples'] = path_checks['coverage']['passed'].retrieve_samples()
        path_checks['coverage']['failed_examples'] = path_checks['coverage']['failed'].retrieve_samples()
        path_checks['quality']['passed_examples'] = path_checks['quality']['passed'].retrieve_samples()
        path_checks['quality']['failed_examples'] = path_checks['quality']['failed'].retrieve_samples()

        del path_checks['coverage']['passed']
        del path_checks['coverage']['failed']
        del path_checks['quality']['passed']
        del path_checks['quality']['failed']

        for check_name, check in path_checks['coverage']['checks'].items():
            check['passed_examples'] = check['passed'].retrieve_samples()
            check['failed_examples'] = check['failed'].retrieve_samples()

            del check['passed']
            del check['failed']

        for check_name, check in path_checks['quality']['checks'].items():
            check['passed_examples'] = check['passed'].retrieve_samples()
            check['failed_examples'] = check['failed'].retrieve_samples()

            del check['passed']
            del check['failed']

        cursor.execute(
            """
            insert into field_level_check_examples
            (dataset_id, path, data)
            values
            ('{}', '{}', '{}');
            """.format(dataset_id, path, json.dumps(path_checks))
        )
    commit()
