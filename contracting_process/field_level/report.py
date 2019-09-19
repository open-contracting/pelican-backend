

import simplejson as json

from tools.db import commit
from tools.db import get_cursor
from tools.helpers import ReservoirSampler
from contracting_process.field_level.definitions import coverage_checks, definitions


def create(dataset_id):
    cursor = get_cursor()
    cursor.execute(
        """
        delete
        from report
        where dataset_id = '{}' and type = '{}';
        """.format(dataset_id, 'field_level_check')
    )

    report = {}

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
                'passed_examples': [],
                'failed_examples': []
            },
            'quality': {
                'checks': {},
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': [],
                'failed_examples': []
            }
        }

        for _, check_name in coverage_checks:
            report[path]['coverage']['checks'][check_name] = {
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': [],
                'failed_examples': []
            }

        for _, check_name in quality_checks:
            report[path]['quality']['checks'][check_name] = {
                'passed_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'passed_examples': [],
                'failed_examples': []
            }
    ################
    # total counts #
    ################

    # coverage
    cursor.execute(
        """
        select sub.path,
               (sub.path_checks->'coverage'->>'overall_result')::boolean as overall_result,
               count(*) as count
        from (
            select d.key as path, jsonb_array_elements(d.value) as path_checks
            from field_level_check, jsonb_each(result->'checks') d
            where dataset_id = '{dataset_id}'
        ) as sub
        where sub.path_checks->'coverage'->>'overall_result' is not null
        group by sub.path, sub.path_checks->'coverage'->>'overall_result';
        """.format(dataset_id=dataset_id)
    )
    for row in cursor.fetchall():
        if row['overall_result'] is True:
            report[row['path']]['coverage']['passed_count'] = row['count']
        elif row['overall_result'] is False:
            report[row['path']]['coverage']['failed_count'] = row['count']
        else:
            raise ValueError(bool)

        report[row['path']]['coverage']['total_count'] += row['count']

    # quality
    cursor.execute(
        """
        select sub.path,
               (sub.path_checks->'quality'->>'overall_result')::boolean as overall_result,
               count(*) as count
        from (
            select d.key as path, jsonb_array_elements(d.value) as path_checks
            from field_level_check, jsonb_each(result->'checks') d
            where dataset_id = '{dataset_id}'
        ) as sub
        where sub.path_checks->'quality'->>'overall_result' is not null
        group by sub.path, sub.path_checks->'quality'->>'overall_result';
        """.format(dataset_id=dataset_id)
    )
    for row in cursor.fetchall():
        if row['overall_result'] is True:
            report[row['path']]['quality']['passed_count'] = row['count']
        elif row['overall_result'] is False:
            report[row['path']]['quality']['failed_count'] = row['count']
        else:
            raise ValueError(bool)

        report[row['path']]['quality']['total_count'] += row['count']

    ##########
    # checks #
    ##########

    # coverage
    cursor.execute(
        """
        select sub1.path, sub1.check->>'name' as name, (sub1.check->>'result')::boolean as result, count(*) as count
        from (
            select sub2.path,
                    jsonb_array_elements(sub2.path_checks->'coverage'->'check_results') as check
            from (
                select jsonb_array_elements(d.value) as path_checks, d.key as path
                from field_level_check, jsonb_each(result->'checks') d
                where dataset_id = '{dataset_id}'
            ) as sub2
            where sub2.path_checks->'coverage'->>'check_results' is not null
        ) as sub1
        group by sub1.path, sub1.check->>'name', sub1.check->>'result';
        """.format(dataset_id=dataset_id)
    )
    for row in cursor.fetchall():
        if row['result'] is True:
            report[row['path']]['coverage']['checks'][row['name']]['passed_count'] = row['count']
        elif row['result'] is False:
            report[row['path']]['coverage']['checks'][row['name']]['failed_count'] = row['count']
        else:
            raise ValueError(bool)

        report[row['path']]['coverage']['checks'][row['name']]['total_count'] += row['count']

    # quality
    cursor.execute(
        """
        select sub1.path, sub1.check->>'name' as name, (sub1.check->>'result')::boolean as result, count(*) as count
        from (
            select sub2.path,
                    jsonb_array_elements(sub2.path_checks->'quality'->'check_results') as check
            from (
                select jsonb_array_elements(d.value) as path_checks, d.key as path
                from field_level_check, jsonb_each(result->'checks') d
                where dataset_id = '{dataset_id}'
            ) as sub2
            where sub2.path_checks->'quality'->>'check_results' is not null
        ) as sub1
        group by sub1.path, sub1.check->>'name', sub1.check->>'result';
        """.format(dataset_id=dataset_id)
    )
    for row in cursor.fetchall():
        if row['result'] is True:
            report[row['path']]['quality']['checks'][row['name']]['passed_count'] = row['count']
        elif row['result'] is False:
            report[row['path']]['quality']['checks'][row['name']]['failed_count'] = row['count']
        else:
            raise ValueError(bool)

        report[row['path']]['quality']['checks'][row['name']]['total_count'] += row['count']

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
