import simplejson as json

from contracting_process.resource_level.definitions import definitions
from tools.db import commit, get_cursor


def create(dataset_id):
    cursor = get_cursor()
    cursor.execute(
        """
        delete
        from report
        where dataset_id = %s and type = %s;
        """,
        [dataset_id, "resource_level_check"],
    )

    report = {}

    for check_name in definitions:
        report[check_name] = {
            "name": check_name,
            "examples_filled": False,
            "passed_count": 0,
            "failed_count": 0,
            "undefined_count": 0,
            "total_count": 0,
            "individual_passed_count": 0,
            "individual_failed_count": 0,
            "individual_application_count": 0,
            "passed_examples": [],
            "failed_examples": [],
            "undefined_examples": [],
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
            where dataset_id = %s
        ) as sub
        group by sub.check_name, sub.result;
        """,
        [dataset_id],
    )

    for row in cursor.fetchall():
        if row["result"] is True:
            report[row["check_name"]]["passed_count"] = row["count"]
        elif row["result"] is False:
            report[row["check_name"]]["failed_count"] = row["count"]
        elif row["result"] is None:
            report[row["check_name"]]["undefined_count"] = row["count"]
        else:
            raise ValueError()

        report[row["check_name"]]["total_count"] += row["count"]

    # individual counts
    cursor.execute(
        """
        select sub.check_name,
               sum(sub.pass_count) as pass_count,
               sum(sub.application_count) as application_count
        from (
            select
                d.key as check_name,
                (d.value->>'pass_count')::int as pass_count,
                (d.value->>'application_count')::int as application_count
            from resource_level_check, jsonb_each(result->'checks') d
            where dataset_id = %s and
                  (
                    case
                        when d.value->'result' is null then null
                        else (d.value->>'result')::boolean
                    end
                  ) is not null
        ) as sub
        group by sub.check_name;
        """,
        [dataset_id],
    )

    for row in cursor.fetchall():
        report[row["check_name"]]["individual_passed_count"] = row["pass_count"]
        report[row["check_name"]]["individual_failed_count"] = row["application_count"] - row["pass_count"]
        report[row["check_name"]]["individual_application_count"] = row["application_count"]

    # storing the report
    cursor.execute(
        """
        insert into report
        (dataset_id, type, data)
        values
        (%s, 'resource_level_check', %s);
        """,
        [dataset_id, json.dumps(report)],
    )
    commit()
