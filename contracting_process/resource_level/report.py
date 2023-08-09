import simplejson as json

from contracting_process.resource_level.definitions import definitions
from pelican.util.services import commit, get_cursor


def create(dataset_id):
    cursor = get_cursor()

    # Delete existing data in case of duplicate messages.
    cursor.execute(
        "DELETE FROM report WHERE dataset_id = %(dataset_id)s and type = 'resource_level_check'",
        {"dataset_id": dataset_id},
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
        """\
        SELECT sub.check_name, sub.result, count(*) AS count
        FROM (
            SELECT
                d.key AS check_name,
                (
                    CASE
                        WHEN d.value->'result' IS NULL THEN NULL
                        ELSE (d.value->>'result')::boolean
                    END
                ) AS result
            FROM resource_level_check, jsonb_each(result->'checks') d
            WHERE dataset_id = %(dataset_id)s
        ) AS sub
        GROUP BY sub.check_name, sub.result
        """,
        {"dataset_id": dataset_id},
    )

    for row in cursor:
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
        """\
        SELECT
            sub.check_name,
            sum(sub.pass_count) AS pass_count,
            sum(sub.application_count) AS application_count
        FROM (
            SELECT
                d.key AS check_name,
                (d.value->>'pass_count')::int AS pass_count,
                (d.value->>'application_count')::int AS application_count
            FROM resource_level_check, jsonb_each(result->'checks') d
            WHERE
                dataset_id = %(dataset_id)s
                AND (
                  CASE
                      WHEN d.value->'result' IS NULL THEN NULL
                      ELSE (d.value->>'result')::boolean
                  END
                ) IS NOT NULL
        ) AS sub
        GROUP BY sub.check_name
        """,
        {"dataset_id": dataset_id},
    )

    for row in cursor:
        report[row["check_name"]]["individual_passed_count"] = row["pass_count"]
        report[row["check_name"]]["individual_failed_count"] = row["application_count"] - row["pass_count"]
        report[row["check_name"]]["individual_application_count"] = row["application_count"]

    cursor.execute(
        "INSERT INTO report (dataset_id, type, data) VALUES (%(dataset_id)s, 'resource_level_check', %(data)s)",
        {"dataset_id": dataset_id, "data": json.dumps(report)},
    )

    commit()

    cursor.close()
