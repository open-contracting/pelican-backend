
import simplejson as json

from tools.db import get_cursor, commit
from tools.logging_helper import get_logger
from tools.helpers import ReservoirSampler
from contracting_process.field_level.definitions import coverage_checks, definitions

examples_cap = 20
page_size = 2000


def create(dataset_id):
    # initialization
    logger = get_logger()
    cursor = get_cursor()

    # house-keeping
    cursor.execute(
        """
        delete
        from report
        where dataset_id = '{}' and type = '{}';
        """.format(dataset_id, 'field_level_check')
    )
    cursor.execute(
        """
        delete
        from field_level_check_examples
        where dataset_id = '{}';
        """.format(dataset_id)
    )

    # creating report and examples
    report = {}
    examples = {}

    for order, definition in enumerate(definitions.items()):
        path, quality_checks = definition

        report[path] = {
            'examples_filled': False,
            'processing_order': order,
            'coverage': {
                'checks': {},
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': None,
                'failed_examples': None
            },
            'quality': {
                'checks': {},
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': None,
                'failed_examples': None
            }
        }

        examples[path] = {
            'coverage': {
                'checks': {},
                'passed_examples': [],
                'failed_examples': [],
                'passed_sampler': ReservoirSampler(examples_cap),
                'failed_sampler': ReservoirSampler(examples_cap)
            },
            'quality': {
                'checks': {},
                'passed_examples': [],
                'failed_examples': [],
                'passed_sampler': ReservoirSampler(examples_cap),
                'failed_sampler': ReservoirSampler(examples_cap)
            }
        }

        for _, check_name in coverage_checks:
            report[path]['coverage']['checks'][check_name] = {
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': None,
                'failed_examples': None
            }

            examples[path]['coverage']['checks'][check_name] = {
                'passed_examples': [],
                'failed_examples': [],
                'passed_sampler': ReservoirSampler(examples_cap),
                'failed_sampler': ReservoirSampler(examples_cap)
            }

        for _, check_name in quality_checks:
            report[path]['quality']['checks'][check_name] = {
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': None,
                'failed_examples': None
            }

            examples[path]['quality']['checks'][check_name] = {
                'passed_examples': [],
                'failed_examples': [],
                'passed_sampler': ReservoirSampler(examples_cap),
                'failed_sampler': ReservoirSampler(examples_cap)
            }

    # processing field level checks
    logger.info("Starting processing pages.")

    processed_count = page_size
    id = -1
    pager = 0

    while processed_count == page_size:
        processed_count = 0
        cursor = get_cursor()

        cursor.execute("""
            SELECT id, result FROM field_level_check
            WHERE
                id > %s
                and dataset_id = %s
            ORDER BY ID
            LIMIT %s
        """, (id, dataset_id, page_size))

        rows = cursor.fetchall()

        for row in rows:
            result = row['result']
            meta = result['meta']

            for path, path_checks in result['checks'].items():
                for path_check in path_checks:
                    exact_path = path_check['path']

                    # coverage
                    if path_check['coverage']['overall_result']:
                        report[path]['coverage']['passed_count'] += 1
                    else:
                        report[path]['coverage']['failed_count'] += 1

                    report[path]['coverage']['total_count'] += 1

                    for check in path_check['coverage']['check_results']:
                        example = {
                            'meta': meta,
                            'path': exact_path,
                            'result': check
                        }

                        if check['result']:
                            report[path]['coverage']['checks'][check['name']]['passed_count'] += 1
                            examples[path]['coverage']['checks'][check['name']]['passed_sampler'].process(example)
                            examples[path]['coverage']['passed_sampler'].process(example)

                        else:
                            report[path]['coverage']['checks'][check['name']]['failed_count'] += 1
                            examples[path]['coverage']['checks'][check['name']]['failed_sampler'].process(example)
                            examples[path]['coverage']['failed_sampler'].process(example)

                        report[path]['coverage']['checks'][check['name']]['total_count'] += 1

                    if not path_check['coverage']['overall_result'] or not path_check['quality']['check_results']:
                        continue

                    # quality
                    if path_check['quality']['overall_result']:
                        report[path]['quality']['passed_count'] += 1
                    else:
                        report[path]['quality']['failed_count'] += 1

                    report[path]['quality']['total_count'] += 1

                    for check in path_check['quality']['check_results']:
                        example = {
                            'meta': meta,
                            'path': exact_path,
                            'result': check
                        }

                        if check['result']:
                            report[path]['quality']['checks'][check['name']]['passed_count'] += 1
                            examples[path]['quality']['checks'][check['name']]['passed_sampler'].process(example)
                            examples[path]['quality']['passed_sampler'].process(example)

                        else:
                            report[path]['quality']['checks'][check['name']]['failed_count'] += 1
                            examples[path]['quality']['checks'][check['name']]['failed_sampler'].process(example)
                            examples[path]['quality']['failed_sampler'].process(example)

                        report[path]['quality']['checks'][check['name']]['total_count'] += 1

            processed_count = processed_count + 1
            id = row["id"]

        pager = pager + 1
        logger.info("Processed page {}".format(pager))

    logger.info("Storing field level check report for dataset_id {}".format(dataset_id))
    # storing the report
    cursor.execute(
        """
        insert into report
        (dataset_id, type, data)
        values
        ('{}', 'field_level_check', '{}');
        """.format(dataset_id, json.dumps(report))
    )
    commit()

    logger.info("Storing examples for field level checks for dataset_id {}".format(dataset_id))
    # storing the examples
    for path, path_checks in examples.items():
        path_checks['coverage']['passed_examples'] = path_checks['coverage']['passed_sampler'].retrieve_samples()
        path_checks['coverage']['failed_examples'] = path_checks['coverage']['failed_sampler'].retrieve_samples()
        path_checks['quality']['passed_examples'] = path_checks['quality']['passed_sampler'].retrieve_samples()
        path_checks['quality']['failed_examples'] = path_checks['quality']['failed_sampler'].retrieve_samples()

        del path_checks['coverage']['passed_sampler']
        del path_checks['coverage']['failed_sampler']
        del path_checks['quality']['passed_sampler']
        del path_checks['quality']['failed_sampler']

        for check_name, check in path_checks['coverage']['checks'].items():
            check['passed_examples'] = check['passed_sampler'].retrieve_samples()
            check['failed_examples'] = check['failed_sampler'].retrieve_samples()

            del check['passed_sampler']
            del check['failed_sampler']

        for check_name, check in path_checks['quality']['checks'].items():
            check['passed_examples'] = check['passed_sampler'].retrieve_samples()
            check['failed_examples'] = check['failed_sampler'].retrieve_samples()

            del check['passed_sampler']
            del check['failed_sampler']

        cursor.execute(
            """
            insert into field_level_check_examples
            (dataset_id, path, data)
            values
            ('{}', '{}', '{}');
            """.format(dataset_id, path, json.dumps(path_checks))
        )
    commit()
