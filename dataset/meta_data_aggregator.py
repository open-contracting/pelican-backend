import logging

import psycopg2.extras
import requests
import simplejson as json

from pelican.util import settings
from pelican.util.getter import get_values, parse_datetime
from pelican.util.services import get_cursor

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

    scope["tender_lifecycle"]["planning"] += len(get_values(item, "planning"))
    scope["tender_lifecycle"]["tender"] += len(get_values(item, "tender"))
    scope["tender_lifecycle"]["award"] += len(get_values(item, "awards"))
    scope["tender_lifecycle"]["contract"] += len(get_values(item, "contracts"))
    scope["tender_lifecycle"]["implementation"] += len(get_values(item, "contracts.implementation"))

    return scope


def get_result(scope):
    scope["compiled_releases"]["total_unique_ocids"] = len(scope["compiled_releases"]["_ocid_set"])
    del scope["compiled_releases"]["_ocid_set"]

    return scope


def get_kingfisher_meta_data(collection_id):
    kf_connection = psycopg2.connect(settings.KINGFISHER_PROCESS_DATABASE_URL)

    kf_cursor = kf_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    meta_data = {
        "kingfisher_metadata": {"collection_id": None, "processing_start": None, "processing_end": None},
        "collection_metadata": {
            "publisher": None,
            "url": None,
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
    meta_data["kingfisher_metadata"] = {}

    # Select whole chain of ascendants of the given child (inclusive). This child must be last in the chain.
    kf_cursor.execute(
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
    result = kf_cursor.fetchall()

    if not result:
        logger.warning("No rows found in `collection` where id = %s", settings.KINGFISHER_PROCESS_DATABASE_URL)
        return meta_data

    meta_data["kingfisher_metadata"]["collection_id"] = collection_id
    # store_start_at of the last record in the chain by deep (first parent)
    meta_data["kingfisher_metadata"]["processing_start"] = result[-1][1].strftime(DATETIME_STR_FORMAT)
    # store_end_at of the first record in the chain by deep (last child)
    meta_data["kingfisher_metadata"]["processing_end"] = result[0][2].strftime(DATETIME_STR_FORMAT)

    ##########################################
    # retrieving additional database entries #
    ##########################################
    proprietary_id = result[-1][0]

    kf_cursor.execute(
        "SELECT * FROM release WHERE collection_id = %(collection_id)s LIMIT 1", {"collection_id": proprietary_id}
    )
    result = kf_cursor.fetchone()
    if result is None:
        kf_cursor.execute(
            "SELECT * FROM record WHERE collection_id = %(collection_id)s LIMIT 1", {"collection_id": proprietary_id}
        )
        result = kf_cursor.fetchone()

    if result is None:
        logger.warning("No rows found in `release` or `record` where collection_id = %s", proprietary_id)
        return meta_data

    kf_cursor.execute(
        "SELECT * FROM package_data WHERE id = %(id)s LIMIT 1",
        {"id": result["package_data_id"]},
    )
    package_data = kf_cursor.fetchone() or {}

    #######################
    # collection metadata #
    #######################

    # publisher
    values = get_values(package_data, "data.publisher.name", value_only=True)
    if values:
        meta_data["collection_metadata"]["publisher"] = values[0]

    # url
    meta_data["collection_metadata"]["url"] = "The URL where the data can be downloaded isn't presently available."

    # ocid prefix
    values = get_values(result, "ocid", value_only=True)
    if values and type(values[0]) == str:
        meta_data["collection_metadata"]["ocid_prefix"] = values[0][:11]

    # data license
    values = get_values(package_data, "data.license", value_only=True)
    if values:
        meta_data["collection_metadata"]["data_license"] = values[0]

    # publication policy
    values = get_values(package_data, "data.publicationPolicy", value_only=True)
    if values:
        meta_data["collection_metadata"]["publication_policy"] = values[0]

    # extensions
    repository_urls = get_values(package_data, "data.extensions", value_only=True)
    for repository_url in repository_urls:
        try:
            response = requests.get(repository_url, timeout=30)
            if response.status_code != 200:
                continue

            extension = response.json()
            extension["repositoryUrl"] = repository_url
            meta_data["collection_metadata"]["extensions"].append(extension)

        except requests.RequestException:
            pass

    # published from, published to
    kf_cursor.execute(
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
    result = kf_cursor.fetchone()

    if result and result[0] and parse_datetime(result[0]):
        meta_data["collection_metadata"]["published_from"] = parse_datetime(result[0]).strftime(DATETIME_STR_FORMAT)
    else:
        meta_data["collection_metadata"]["published_from"] = None

    if result and result[1] and parse_datetime(result[1]):
        meta_data["collection_metadata"]["published_to"] = parse_datetime(result[1]).strftime(DATETIME_STR_FORMAT)
    else:
        meta_data["collection_metadata"]["published_to"] = None

    kf_cursor.close()
    kf_connection.close()

    return meta_data


def get_dqt_meta_data(dataset_id):
    meta_data = {"data_quality_tool_metadata": {"processing_start": None, "processing_end": None}}

    with get_cursor() as cursor:
        cursor.execute("SELECT created, now() FROM dataset WHERE id = %(id)s", {"id": dataset_id})
        row = cursor.fetchone()

    meta_data["data_quality_tool_metadata"]["processing_start"] = row[0].strftime(DATETIME_STR_FORMAT)
    meta_data["data_quality_tool_metadata"]["processing_end"] = row[1].strftime(DATETIME_STR_FORMAT)

    return meta_data


def update_meta_data(meta_data, dataset_id):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE dataset SET meta = meta || %(meta)s, modified = now() WHERE id = %(id)s",
            {"meta": json.dumps(meta_data), "id": dataset_id},
        )
