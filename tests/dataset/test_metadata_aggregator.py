from dataset.metadata_aggregator import add_item, get_kingfisher_metadata, get_result
from pelican.util.currency_converter import bootstrap

bootstrap()


items_test_compiled_releases = [
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00"},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00"},
    {"ocid": "1", "date": "2019-01-10T22:00:00+01:00"},
]


items_test_tender_lifecycle = [
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "planning": {}, "tender": {}},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "tender": {}},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "awards": [{}, {}, {}]},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "contracts": [{}, {}, {}]},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "contracts": [{"implementation": {}}]},
]


def create_compiled_release(cursor, collection_id, collection_file_id, data_rows):
    min_data_id, max_data_id = data_rows

    cursor.execute(
        """\
        INSERT INTO compiled_release (
            ocid,
            collection_id,
            collection_file_id,
            data_id,
            release_date
        ) VALUES (
            'ocds-lcuori-1',
            %(collection_id)s,
            %(collection_file_id)s,
            %(max_data_id)s,
            '2038'
        ), (
            'ocds-lcuori-1',
            %(collection_id)s,
            %(collection_file_id)s,
            %(min_data_id)s,
            '1970'
        )
        """,
        {
            "collection_id": collection_id,
            "collection_file_id": collection_file_id,
            "min_data_id": min_data_id,
            "max_data_id": max_data_id,
        },
    )


def test_compiled_releases():
    scope = {}
    for item_id in range(len(items_test_compiled_releases)):
        scope = add_item(scope, items_test_compiled_releases[item_id], item_id)
    result = get_result(scope)

    assert result["compiled_releases"]["total_unique_ocids"] == 2
    assert sum(result["tender_lifecycle"].values()) == 0


def test_tender_lifecycle():
    scope = {}
    for item_id in range(len(items_test_tender_lifecycle)):
        scope = add_item(scope, items_test_tender_lifecycle[item_id], item_id)
    result = get_result(scope)

    assert result["compiled_releases"]["total_unique_ocids"] == 1
    assert result["tender_lifecycle"] == {"planning": 1, "tender": 2, "award": 3, "contract": 4, "implementation": 1}


def test_get_kingfisher_metadata_nonexistent(kingfisher_process_cursor, caplog):
    assert get_kingfisher_metadata(kingfisher_process_cursor, 999999999) == {
        "collection_metadata": {
            "data_license": None,
            "extensions": [],
            "ocid_prefix": None,
            "publication_policy": None,
            "published_from": None,
            "published_to": None,
            "publisher": None,
        },
        "kingfisher_metadata": {},
    }

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == "No rows found in `collection` where id = 999999999"


def test_get_kingfisher_metadata_tree(kingfisher_process_cursor, collection_rows, caplog):
    original, compiled = collection_rows

    assert get_kingfisher_metadata(kingfisher_process_cursor, compiled) == {
        "collection_metadata": {
            "data_license": None,
            "extensions": [],
            "ocid_prefix": None,
            "publication_policy": None,
            "published_from": None,
            "published_to": None,
            "publisher": None,
        },
        "kingfisher_metadata": {
            "collection_id": compiled,
            "processing_end": "2001-02-03 07.08.09",
            "processing_start": "2001-02-03 04.05.06",
        },
    }

    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == f"No rows found in `compiled_release` where collection_id = {compiled}"
    assert caplog.records[-1].levelname == "WARNING"
    assert caplog.records[-1].message == f"No rows found in `release` or `record` where collection_id = {original}"


def test_get_kingfisher_metadata_compiled_release(
    kingfisher_process_cursor, collection_rows, collection_file, data_rows, caplog
):
    original, compiled = collection_rows

    create_compiled_release(kingfisher_process_cursor, compiled, collection_file, data_rows)

    assert get_kingfisher_metadata(kingfisher_process_cursor, compiled) == {
        "collection_metadata": {
            "data_license": None,
            "extensions": [],
            "ocid_prefix": "ocds-lcuori",
            "publication_policy": None,
            "published_from": "1970-01-01 00.00.00",
            "published_to": "2038-01-01 00.00.00",
            "publisher": None,
        },
        "kingfisher_metadata": {
            "collection_id": compiled,
            "processing_end": "2001-02-03 07.08.09",
            "processing_start": "2001-02-03 04.05.06",
        },
    }

    assert len(caplog.records) == 1
    assert caplog.records[-1].levelname == "WARNING"
    assert caplog.records[-1].message == f"No rows found in `release` or `record` where collection_id = {original}"


def test_get_kingfisher_metadata_release(
    kingfisher_process_cursor, collection_rows, collection_file, data_rows, data_and_package_data_rows, caplog
):
    original, compiled = collection_rows

    create_compiled_release(kingfisher_process_cursor, compiled, collection_file, data_rows)

    data_id, package_data_id = data_and_package_data_rows

    kingfisher_process_cursor.execute(
        """\
        INSERT INTO release (
            release_id,
            ocid,
            collection_id,
            collection_file_id,
            data_id,
            package_data_id,
            release_date
        ) VALUES (
            '1',
            'ocds-lcuori-1',
            %(collection_id)s,
            %(collection_file_id)s,
            %(data_id)s,
            %(package_data_id)s,
            ''
        )
        """,
        {
            "collection_id": original,
            "collection_file_id": collection_file,
            "data_id": data_id,
            "package_data_id": package_data_id,
        },
    )

    assert get_kingfisher_metadata(kingfisher_process_cursor, compiled) == {
        "collection_metadata": {
            "data_license": "https://creativecommons.org/licenses/by/4.0/",
            "extensions": [
                {
                    "compatibility": ["1.1"],
                    "contactPoint": {
                        "email": "data@open-contracting.org",
                        "name": "Open Contracting Partnership",
                    },
                    "description": {
                        "en": "For providing overall process titles and descriptions, often to give a summary of the contracting process as a whole.",  # noqa: E501
                    },
                    "documentationUrl": {"en": "https://extensions.open-contracting.org/en/extensions/process_title/"},
                    "name": {"en": "Process level title and description"},
                    "repositoryUrl": "https://raw.githubusercontent.com/open-contracting-extensions/ocds_process_title_extension/master/extension.json",
                    "schemas": ["release-schema.json"],
                },
            ],
            "ocid_prefix": "ocds-lcuori",
            "publication_policy": "https://example.com/policy",
            "published_from": "1970-01-01 00.00.00",
            "published_to": "2038-01-01 00.00.00",
            "publisher": "Acme Inc.",
        },
        "kingfisher_metadata": {
            "collection_id": compiled,
            "processing_end": "2001-02-03 07.08.09",
            "processing_start": "2001-02-03 04.05.06",
        },
    }

    assert len(caplog.records) == 0


def test_get_kingfisher_metadata_record(
    kingfisher_process_cursor, collection_rows, collection_file, data_rows, data_and_package_data_rows, caplog
):
    original, compiled = collection_rows

    create_compiled_release(kingfisher_process_cursor, compiled, collection_file, data_rows)

    data_id, package_data_id = data_and_package_data_rows

    kingfisher_process_cursor.execute(
        """\
        INSERT INTO record (
            ocid,
            collection_id,
            collection_file_id,
            data_id,
            package_data_id
        ) VALUES (
            'ocds-lcuori-1',
            %(collection_id)s,
            %(collection_file_id)s,
            %(data_id)s,
            %(package_data_id)s
        )
        """,
        {
            "collection_id": original,
            "collection_file_id": collection_file,
            "data_id": data_id,
            "package_data_id": package_data_id,
        },
    )

    assert get_kingfisher_metadata(kingfisher_process_cursor, compiled) == {
        "collection_metadata": {
            "data_license": "https://creativecommons.org/licenses/by/4.0/",
            "extensions": [
                {
                    "compatibility": ["1.1"],
                    "contactPoint": {
                        "email": "data@open-contracting.org",
                        "name": "Open Contracting Partnership",
                    },
                    "description": {
                        "en": "For providing overall process titles and descriptions, often to give a summary of the contracting process as a whole.",  # noqa: E501
                    },
                    "documentationUrl": {"en": "https://extensions.open-contracting.org/en/extensions/process_title/"},
                    "name": {"en": "Process level title and description"},
                    "repositoryUrl": "https://raw.githubusercontent.com/open-contracting-extensions/ocds_process_title_extension/master/extension.json",
                    "schemas": ["release-schema.json"],
                },
            ],
            "ocid_prefix": "ocds-lcuori",
            "publication_policy": "https://example.com/policy",
            "published_from": "1970-01-01 00.00.00",
            "published_to": "2038-01-01 00.00.00",
            "publisher": "Acme Inc.",
        },
        "kingfisher_metadata": {
            "collection_id": compiled,
            "processing_end": "2001-02-03 07.08.09",
            "processing_start": "2001-02-03 04.05.06",
        },
    }

    assert len(caplog.records) == 0
