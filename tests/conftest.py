import json
import os

import psycopg2.extras
import pytest
from jsonschema import FormatChecker

from pelican.util import settings


@pytest.fixture(scope="session")
def schema():
    # From standard-maintenance-scripts/tests/test_readme.py
    def set_additional_properties_false(data):
        if isinstance(data, list):
            for item in data:
                set_additional_properties_false(item)
        elif isinstance(data, dict):
            if "properties" in data:
                data["additionalProperties"] = False
            for value in data.values():
                set_additional_properties_false(value)

    with open(os.path.join("pelican", "static", "release-schema.json")) as f:
        schema = json.load(f)

    set_additional_properties_false(schema)

    return schema


@pytest.fixture(scope="session")
def format_checker():
    return FormatChecker()


@pytest.fixture(scope="session")
def kingfisher_process_cursor():
    connection = psycopg2.connect(settings.KINGFISHER_PROCESS_DATABASE_URL)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    with open(os.path.join("tests", "fixtures", "kingfisher_process.sql")) as f:
        cursor.execute(f.read())

    return cursor


@pytest.fixture(scope="session")
def collection_rows(kingfisher_process_cursor):
    kingfisher_process_cursor.execute(
        """\
        INSERT INTO collection (
            source_id,
            data_version,
            sample,
            transform_type,
            scrapyd_job,
            steps,
            options,
            data_type,
            compilation_started,
            store_start_at,
            store_end_at
        ) VALUES (
            'pytest',
            '1970-01-01 00:00:00',
            false,
            '',
            '',
            '[]'::jsonb,
            '{}'::jsonb,
            '{}'::jsonb,
            false,
            '2001-02-03 04:05:06',
            '9999-12-31 23:59:59'
        )
        """
    )
    kingfisher_process_cursor.execute("SELECT id FROM collection WHERE source_id = 'pytest'")
    original = kingfisher_process_cursor.fetchone()["id"]

    kingfisher_process_cursor.execute(
        """\
        INSERT INTO collection (
            source_id,
            data_version,
            sample,
            transform_from_collection_id,
            transform_type,
            scrapyd_job,
            steps,
            options,
            data_type,
            compilation_started,
            store_start_at,
            store_end_at
        ) VALUES (
            'pytest',
            '1970-01-01 00:00:00',
            false,
            %(collection_id)s,
            'compile-releases',
            '',
            '[]'::jsonb,
            '{}'::jsonb,
            '{}'::jsonb,
            false,
            '0001-01-01 00:00:00',
            '2001-02-03 07:08:09'
        )
        """,
        {"collection_id": original},
    )
    kingfisher_process_cursor.execute("SELECT id FROM collection WHERE source_id = 'pytest' AND transform_type <> ''")
    compiled = kingfisher_process_cursor.fetchone()["id"]

    return original, compiled


@pytest.fixture(scope="session")
def collection_file(kingfisher_process_cursor, collection_rows):
    kingfisher_process_cursor.execute(
        """\
        INSERT INTO collection_file (
            filename,
            url,
            collection_id
        ) VALUES (
            'test.json',
            'https://example.com/test.json',
            %(collection_id)s
        )
        """,
        {"collection_id": collection_rows[1]},
    )
    kingfisher_process_cursor.execute("SELECT MAX(id) FROM collection_file")
    return kingfisher_process_cursor.fetchone()[0]


@pytest.fixture(scope="session")
def data_rows(kingfisher_process_cursor):
    kingfisher_process_cursor.execute(
        """\
        INSERT INTO data (
            hash_md5,
            data
        ) VALUES (
            'min',
            '{"ocid": "ocds-lcuori-1", "date": "1970"}'::jsonb
        )
        """
    )
    kingfisher_process_cursor.execute("SELECT MAX(id) FROM data")
    min_data_id = kingfisher_process_cursor.fetchone()[0]

    kingfisher_process_cursor.execute(
        """\
        INSERT INTO data (
            hash_md5,
            data
        ) VALUES (
            'max',
            '{"ocid": "ocds-lcuori-1", "date": "2038"}'::jsonb
        )
        """
    )
    kingfisher_process_cursor.execute("SELECT MAX(id) FROM data")
    max_data_id = kingfisher_process_cursor.fetchone()[0]

    return min_data_id, max_data_id


@pytest.fixture(scope="session")
def data_and_package_data_rows(kingfisher_process_cursor):
    kingfisher_process_cursor.execute(
        """\
        INSERT INTO data (
            hash_md5,
            data
        ) VALUES (
            'empty',
            '{}'::jsonb
        )
        """
    )
    kingfisher_process_cursor.execute("SELECT MAX(id) FROM data")
    data_id = kingfisher_process_cursor.fetchone()[0]

    kingfisher_process_cursor.execute(
        """\
        INSERT INTO package_data (
            hash_md5,
            data
        ) VALUES (
            'package',
            %(data)s::jsonb
        )
        """,
        {
            "data": json.dumps(
                {
                    "publisher": {"name": "Acme Inc."},
                    "license": "https://creativecommons.org/licenses/by/4.0/",
                    "publicationPolicy": "https://example.com/policy",
                    "extensions": [
                        "https://raw.githubusercontent.com/open-contracting-extensions/ocds_process_title_extension/master/extension.json",
                    ],
                }
            )
        },
    )
    kingfisher_process_cursor.execute("SELECT MAX(id) FROM package_data")
    package_data_id = kingfisher_process_cursor.fetchone()[0]

    return data_id, package_data_id
