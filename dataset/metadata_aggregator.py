import logging

import requests

from pelican.util.getter import deep_get, deep_has, get_values, parse_datetime
from pelican.util.services import Json, get_cursor

DATE_STR_FORMAT = "%b-%-y"
DATETIME_STR_FORMAT = "%Y-%m-%d %H.%M.%S"

logger = logging.getLogger(__name__)


def add_item(scope, item, item_id):
    if not scope:
        scope = {
            "compiled_releases": {"total_unique_ocids": None, "_ocid_set": set()},
            "tender_lifecycle": {"planning": 0, "tender": 0, "award": 0, "contract": 0, "implementation": 0},
        }

    scope["compiled_releases"]["_ocid_set"].add(item["ocid"])

    scope["tender_lifecycle"]["planning"] += deep_has(item, "planning")
    scope["tender_lifecycle"]["tender"] += deep_has(item, "tender")
    scope["tender_lifecycle"]["award"] += len(deep_get(item, "awards", list))
    scope["tender_lifecycle"]["contract"] += len(deep_get(item, "contracts", list))
    scope["tender_lifecycle"]["implementation"] += len(get_values(item, "contracts.implementation"))

    return scope


def get_result(scope):
    scope["compiled_releases"]["total_unique_ocids"] = len(scope["compiled_releases"]["_ocid_set"])
    del scope["compiled_releases"]["_ocid_set"]

    return scope


def get_kingfisher_metadata(kingfisher_process_cursor, collection_id):
    metadata = {
        "kingfisher_metadata": {"collection_id": None, "processing_start": None, "processing_end": None},
        "collection_metadata": {
            "publisher": None,
            "ocid_prefix": None,
            "data_license": None,
            "publication_policy": None,
            "extensions": [],
            "published_from": None,
            "published_to": None,
        },
    }

    #######################
    # kingfisher metadata #
    #######################
    metadata["kingfisher_metadata"] = {}

    # Select whole chain of ascendants of the given child (inclusive). This child must be last in the chain.
    kingfisher_process_cursor.execute(
        """\
        WITH RECURSIVE tree(id, parent, root, deep) AS (
            SELECT c.id, c.transform_from_collection_id AS parent, c.id AS root, 1 AS deep
            FROM collection c
            LEFT JOIN collection c2 ON c2.transform_from_collection_id = c.id
            WHERE c2 IS NULL
        UNION ALL
            SELECT c.id, c.transform_from_collection_id, t.root, t.deep + 1
            FROM collection c, tree t
            WHERE c.id = t.parent
        )
        SELECT c.id, c.store_start_at, c.store_end_at
        FROM tree t
        JOIN collection c on t.id = c.id
        WHERE t.root = %(root)s
        ORDER BY deep ASC
        """,
        {"root": collection_id},
    )
    tree = kingfisher_process_cursor.fetchall()

    if not tree:
        logger.warning("No rows found in `collection` where id = %s", collection_id)
        return metadata

    metadata["kingfisher_metadata"]["collection_id"] = collection_id
    # store_start_at of the last record in the chain by deep (first parent)
    metadata["kingfisher_metadata"]["processing_start"] = tree[-1][1].strftime(DATETIME_STR_FORMAT)
    # store_end_at of the first record in the chain by deep (last child)
    metadata["kingfisher_metadata"]["processing_end"] = tree[0][2].strftime(DATETIME_STR_FORMAT)

    ##############################################
    # collection metadata from compiled releases #
    ##############################################

    kingfisher_process_cursor.execute(
        """\
        SELECT MIN(data.data->>'date'), MAX(data.data->>'date')
        FROM compiled_release
        JOIN data ON compiled_release.data_id = data.id
        WHERE
            compiled_release.collection_id = %(collection_id)s
            AND data.data ? 'date'
            AND data.data->>'date' IS NOT NULL
            AND data.data->>'date' <> ''
        LIMIT 1
        """,
        {"collection_id": collection_id},
    )
    dates = kingfisher_process_cursor.fetchone()

    if dates:
        for index, key in enumerate(("published_from", "published_to")):
            value = parse_datetime(dates[index])
            if value:
                metadata["collection_metadata"][key] = value.strftime(DATETIME_STR_FORMAT)

    #####################################
    # collection metadata from packages #
    #####################################

    root_id = tree[-1][0]

    kingfisher_process_cursor.execute(
        "SELECT * FROM release WHERE collection_id = %(collection_id)s LIMIT 1", {"collection_id": root_id}
    )
    release_or_record = kingfisher_process_cursor.fetchone()
    if not release_or_record:
        kingfisher_process_cursor.execute(
            "SELECT * FROM record WHERE collection_id = %(collection_id)s LIMIT 1", {"collection_id": root_id}
        )
        release_or_record = kingfisher_process_cursor.fetchone()

    if not release_or_record:
        logger.warning("No rows found in `release` or `record` where collection_id = %s", root_id)
        return metadata

    metadata["collection_metadata"]["ocid_prefix"] = release_or_record["ocid"][:11]

    kingfisher_process_cursor.execute(
        "SELECT data FROM package_data WHERE id = %(id)s LIMIT 1",
        {"id": release_or_record["package_data_id"]},
    )
    package_data_row = kingfisher_process_cursor.fetchone()

    if package_data_row:
        package_data = package_data_row["data"]
        if value := deep_get(package_data, "publisher.name"):
            metadata["collection_metadata"]["publisher"] = value

        if value := deep_get(package_data, "license"):
            metadata["collection_metadata"]["data_license"] = value

        if value := deep_get(package_data, "publicationPolicy"):
            metadata["collection_metadata"]["publication_policy"] = value

        for repository_url in deep_get(package_data, "extensions", list):
            try:
                response = requests.get(repository_url, timeout=30)
                if response.status_code != 200:
                    continue

                extension = response.json()
                extension["repositoryUrl"] = repository_url
                metadata["collection_metadata"]["extensions"].append(extension)
            except requests.RequestException:
                pass

    return metadata


def get_pelican_metadata(dataset_id):
    metadata = {"data_quality_tool_metadata": {"processing_start": None, "processing_end": None}}

    with get_cursor() as cursor:
        cursor.execute("SELECT created, now() FROM dataset WHERE id = %(id)s", {"id": dataset_id})
        row = cursor.fetchone()

    metadata["data_quality_tool_metadata"]["processing_start"] = row[0].strftime(DATETIME_STR_FORMAT)
    metadata["data_quality_tool_metadata"]["processing_end"] = row[1].strftime(DATETIME_STR_FORMAT)

    return metadata


def update_metadata(metadata, dataset_id):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE dataset SET meta = meta || %(meta)s, modified = now() WHERE id = %(id)s",
            {"meta": Json(metadata), "id": dataset_id},
        )
