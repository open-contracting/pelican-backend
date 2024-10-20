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
    """
    Return metadata from Kingfisher Process.

    :param kingfisher_process_cursor: the cursor must be initialized with `cursor_factory=psycopg2.extras.DictCursor`
    :param collection_id: the ID of the compiled collection
    """
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
        WITH RECURSIVE tree (
            id,
            transform_from_collection_id,
            leaf,
            deep
        ) AS (
            SELECT
                collection.id,
                collection.transform_from_collection_id,
                collection.id AS leaf,
                1 AS deep
            FROM
                collection
                LEFT JOIN collection child ON child.transform_from_collection_id = collection.id
            WHERE
                child IS NULL
            UNION ALL
            SELECT
                collection.id,
                collection.transform_from_collection_id,
                tree.leaf,
                tree.deep + 1
            FROM
                collection
                JOIN tree ON tree.transform_from_collection_id = collection.id
        )
        SELECT
            collection.id,
            store_start_at,
            store_end_at
        FROM
            tree
            JOIN collection ON collection.id = tree.id
        WHERE
            tree.leaf = %(collection_id)s
        ORDER BY
            deep ASC
        """,
        {"collection_id": collection_id},
    )
    tree = kingfisher_process_cursor.fetchall()

    if not tree:
        logger.warning("No rows found in `collection` where id = %s", collection_id)
        return metadata

    metadata["kingfisher_metadata"]["collection_id"] = collection_id
    metadata["kingfisher_metadata"]["processing_start"] = tree[-1][1].strftime(DATETIME_STR_FORMAT)
    metadata["kingfisher_metadata"]["processing_end"] = tree[0][2].strftime(DATETIME_STR_FORMAT)

    ##############################################
    # collection metadata from compiled releases #
    ##############################################

    kingfisher_process_cursor.execute(
        """\
        SELECT
            LEFT(MAX(ocid), 11) AS ocid_prefix,
            MIN(release_date) AS published_from,
            MAX(release_date) AS published_to
        FROM
            compiled_release
        WHERE
            collection_id = %(collection_id)s
            AND release_date <> ''
        """,
        {"collection_id": collection_id},
    )

    row = kingfisher_process_cursor.fetchone()

    if any(row):
        metadata["collection_metadata"]["ocid_prefix"] = row["ocid_prefix"]
        for key in ("published_from", "published_to"):
            if value := parse_datetime(row[key]):
                metadata["collection_metadata"][key] = value.strftime(DATETIME_STR_FORMAT)
    else:
        logger.warning("No rows found in `compiled_release` where collection_id = %s", collection_id)

    #####################################
    # collection metadata from packages #
    #####################################

    original_collection_id = tree[-1][0]

    kingfisher_process_cursor.execute(
        """\
        SELECT
            data,
            data -> 'publisher' ->> 'name' AS publisher,
            data ->> 'license' AS data_license,
            data ->> 'publicationPolicy' AS publication_policy
        FROM (
            (
                SELECT
                    data
                FROM
                    package_data
                    JOIN record ON package_data_id = package_data.id
                WHERE
                    collection_id = %(collection_id)s
                LIMIT 1
            )
            UNION ALL
            (
                SELECT
                    data
                FROM
                    package_data
                    JOIN release ON package_data_id = package_data.id
                WHERE
                    collection_id = %(collection_id)s
                LIMIT 1
            )
        ) t
        """,
        {"collection_id": original_collection_id},
    )

    if row := kingfisher_process_cursor.fetchone():
        for key in ("publisher", "data_license", "publication_policy"):
            if row[key]:
                metadata["collection_metadata"][key] = row[key]

        for extension_url in deep_get(row["data"], "extensions", list):
            try:
                # Security: Potential SSRF via user-provided URL (within OCDS publication).
                response = requests.get(extension_url, timeout=30)
                if response.status_code != requests.codes.ok:
                    continue

                extension = response.json()
                extension["repositoryUrl"] = extension_url
                metadata["collection_metadata"]["extensions"].append(extension)
            except requests.RequestException:
                pass
    else:
        logger.warning("No rows found in `release` or `record` where collection_id = %s", original_collection_id)

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
