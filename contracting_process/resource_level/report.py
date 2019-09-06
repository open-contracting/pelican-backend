
import simplejson as json

from tools.db import commit
from tools.db import get_cursor
from tools.helpers import ReservoirSampler
from contracting_process.resource_level.definitions import definitions


def create(dataset_id):
    cursor = get_cursor()
    cursor.execute(
        """
        delete
        from report
        where dataset_id = '{}' and type = '{}';
        """.format(dataset_id, 'resource_level_check')
    )

    report = {}

    for check_name in definitions:
        report[check_name] = {
            'examples_filled': False,
            'passed_count': 0,
            'failed_count': 0,
            'undefined_count': 0,
            'total_count': 0,
            'passed_examples': [],
            'failed_examples': [],
            'undefined_examples': []
        }

    # total counts
    cursor.execute(
        """
        select sub.check_name, sub.result, count(*) as count
        from (
            select
                d.key as check_name,
                (
                    case
                        when d.value->'result' is null then null
                        else (d.value->>'result')::boolean
                    end
                ) as result
            from resource_level_check, jsonb_each(result->'checks') d
            where dataset_id = '{dataset_id}'
        ) as sub
        group by sub.check_name, sub.result;
        """.format(dataset_id=dataset_id)
    )

    for row in cursor.fetchall():
        if row['result'] is True:
            report[row['check_name']]['passed_count'] = row['count']
        elif row['result'] is False:
            report[row['check_name']]['failed_count'] = row['count']
        elif row['result'] is None:
            report[row['check_name']]['undefined_count'] = row['count']
        else:
            raise ValueError()

        report[row['check_name']]['total_count'] += row['count']

    # storing the report
    cursor.execute(
        """
        insert into report
        (dataset_id, type, data)
        values
        ('{}', 'resource_level_check', '{}');
        """.format(dataset_id, json.dumps(report))
    )
    commit()
