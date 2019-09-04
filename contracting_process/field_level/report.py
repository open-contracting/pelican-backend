

import simplejson as json

from tools.db import commit
from tools.db import get_cursor
from tools.helpers import ReservoirSampler
from contracting_process.field_level.definitions import coverage_checks, definitions

check_examples_cap = 10


def create(dataset_id):
    cursor = get_cursor()

    report = {}

    for path, quality_checks in definitions.items():
        report[path] = {
            'coverage': {
                'checks': [

                ],
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': [],
                'failed_examples': []
            },
            'quality': {
                'checks': [

                ],
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': [],
                'failed_examples': []
            }
        }

        ############
        # coverage #
        ############

        # total counts
        cursor.execute(
            """
            select distinct (sub.path->'coverage'->>'overall_result')::boolean, count(*)
            from (
                select jsonb_array_elements(d.value) as path
                from field_level_check, jsonb_each(result->'checks') d
                where dataset_id = '{dataset_id}' and d.key = '{path}'
            ) as sub
            where sub.path->'coverage'->>'overall_result' is not null
            group by sub.path->'coverage'->>'overall_result';
            """.format(dataset_id=dataset_id, path=path)
        )
        for row in cursor.fetchall():
            if row[0] is True:
                report[path]['coverage']['passed_count'] = row[1]
            elif row[0] is False:
                report[path]['coverage']['failed_count'] = row[1]
            else:
                raise ValueError(bool)

            report[path]['coverage']['total_count'] += row[1]

        # checks
        coverage_passed_examples_sampler = ReservoirSampler(check_examples_cap)
        coverage_failed_examples_sampler = ReservoirSampler(check_examples_cap)
        for check, check_name in coverage_checks:
            check_meta = {
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': [],
                'failed_examples': []
            }
            check_passed_examples_sampler = ReservoirSampler(check_examples_cap)
            check_failed_examples_sampler = ReservoirSampler(check_examples_cap)

            cursor.execute(
                """
                select sub1.meta, sub1.path, sub1.check
                from (
                    select sub2.meta,
                           sub2.path->>'path' as path,
                           jsonb_array_elements(sub2.path->'coverage'->'check_results') as check
                    from (
                        select result->'meta' as meta, jsonb_array_elements(d.value) as path
                        from field_level_check, jsonb_each(result->'checks') d
                        where dataset_id = '{dataset_id}' and d.key = '{path}'
                    ) as sub2
                    where sub2.path->'coverage'->>'check_results' is not null
                ) as sub1
                where sub1.check->>'name' = '{check_name}';
                """.format(dataset_id=dataset_id, path=path, check_name=check_name)
            )

            for row in cursor.fetchall():
                example = {
                    'meta': row['meta'],
                    'result': row['check']
                }
                example['meta']['path'] = row['path']

                if row['check']['result']:
                    coverage_passed_examples_sampler.process(example)
                    check_passed_examples_sampler.process(example)

                    check_meta['passed_count'] += 1
                else:
                    coverage_failed_examples_sampler.process(example)
                    check_failed_examples_sampler.process(example)

                    check_meta['failed_count'] += 1

                check_meta['total_count'] += 1

            check_meta['passed_examples'] = check_passed_examples_sampler.retrieve_samples()
            check_meta['failed_examples'] = check_failed_examples_sampler.retrieve_samples()
            report[path]['coverage']['checks'].append(check_meta)

        report[path]['coverage']['passed_examples'] = coverage_passed_examples_sampler.retrieve_samples()
        report[path]['coverage']['failed_examples'] = coverage_failed_examples_sampler.retrieve_samples()

        ###########
        # quality #
        ###########

        # total counts
        cursor.execute(
            """
            select distinct (sub.path->'quality'->>'overall_result')::boolean, count(*)
            from (
                select jsonb_array_elements(d.value) as path
                from field_level_check, jsonb_each(result->'checks') d
                where dataset_id = '{dataset_id}' and d.key = '{path}'
            ) as sub
            where sub.path->'quality'->>'overall_result' is not null
            group by sub.path->'quality'->>'overall_result';
            """.format(dataset_id=dataset_id, path=path)
        )
        for row in cursor.fetchall():
            if row[0] is True:
                report[path]['quality']['passed_count'] = row[1]
            elif row[0] is False:
                report[path]['quality']['failed_count'] = row[1]
            else:
                raise ValueError(bool)

            report[path]['quality']['total_count'] += row[1]

        # checks
        quality_passed_examples_sampler = ReservoirSampler(check_examples_cap)
        quality_failed_examples_sampler = ReservoirSampler(check_examples_cap)
        for check, check_name in quality_checks:
            check_meta = {
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': [],
                'failed_examples': []
            }
            check_passed_examples_sampler = ReservoirSampler(check_examples_cap)
            check_failed_examples_sampler = ReservoirSampler(check_examples_cap)

            cursor.execute(
                """
                select sub1.meta, sub1.path, sub1.check
                from (
                    select sub2.meta,
                           sub2.path->>'path' as path,
                           jsonb_array_elements(sub2.path->'quality'->'check_results') as check
                    from (
                        select result->'meta' as meta, jsonb_array_elements(d.value) as path
                        from field_level_check, jsonb_each(result->'checks') d
                        where dataset_id = '{dataset_id}' and d.key = '{path}'
                    ) as sub2
                    where sub2.path->'quality'->>'check_results' is not null
                ) as sub1
                where sub1.check->>'name' = '{check_name}';
                """.format(dataset_id=dataset_id, path=path, check_name=check_name)
            )

            for row in cursor.fetchall():
                example = {
                    'meta': row['meta'],
                    'result': row['check']
                }
                example['meta']['path'] = row['path']

                if row['check']['result']:
                    quality_passed_examples_sampler.process(example)
                    check_passed_examples_sampler.process(example)

                    check_meta['passed_count'] += 1
                else:
                    quality_failed_examples_sampler.process(example)
                    check_failed_examples_sampler.process(example)

                    check_meta['failed_count'] += 1

                check_meta['total_count'] += 1

            check_meta['passed_examples'] = check_passed_examples_sampler.retrieve_samples()
            check_meta['failed_examples'] = check_failed_examples_sampler.retrieve_samples()
            report[path]['quality']['checks'].append(check_meta)

        report[path]['quality']['passed_examples'] = quality_passed_examples_sampler.retrieve_samples()
        report[path]['quality']['failed_examples'] = quality_failed_examples_sampler.retrieve_samples()

    ######################
    # storing the report #
    ######################
    cursor.execute(
        """
        insert into report
        (dataset_id, type, data)
        values
        ('{}', 'field_level_check', '{}');
        """.format(dataset_id, json.dumps(report))
    )
    commit()
