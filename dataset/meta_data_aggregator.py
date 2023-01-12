import psycopg2.extras
import requests
import simplejson as json
from dateutil.relativedelta import relativedelta

from tools import settings
from tools.currency_converter import convert
from tools.getter import get_values
from tools.helpers import parse_datetime
from tools.services import get_cursor

DATE_STR_FORMAT = "%b-%-y"
DATETIME_STR_FORMAT = "%Y-%m-%d %H.%M.%S"


def add_item(scope, item, item_id):
    if not scope:
        scope = {
            "compiled_releases": {"total_unique_ocids": None, "_ocid_set": set()},
            "tender_lifecycle": {"planning": 0, "tender": 0, "award": 0, "contract": 0, "implementation": 0},
            "prices": {
                "total_volume_positive": 0,
                "contracts_positive": 0,
                "total_volume_negative": 0,
                "contracts_negative": 0,
                "price_category_positive": {
                    "0_10000": {"contracts": 0, "volume": 0, "share": None},
                    "10001_100000": {"contracts": 0, "volume": 0, "share": None},
                    "100001_1000000": {"contracts": 0, "volume": 0, "share": None},
                    "1000001+": {"contracts": 0, "volume": 0, "share": None},
                },
            },
            "_period_dict": {},
            "period": None,
        }

    # compiled releases
    scope["compiled_releases"]["_ocid_set"].add(item["ocid"])

    # tender lifecycle
    scope["tender_lifecycle"]["planning"] += len(get_values(item, "planning"))
    scope["tender_lifecycle"]["tender"] += len(get_values(item, "tender"))
    scope["tender_lifecycle"]["award"] += len(get_values(item, "awards"))
    scope["tender_lifecycle"]["contract"] += len(get_values(item, "contracts"))
    scope["tender_lifecycle"]["implementation"] += len(get_values(item, "contracts.implementation"))

    # prices
    rel_date = None
    if "date" in item:
        rel_datetime = parse_datetime(item["date"])
        rel_date = rel_datetime.date() if rel_datetime else None
    values = get_values(item, "contracts.value", value_only=True)
    for value in values:
        # check whether relevant field are set
        if "amount" not in value or "currency" not in value or value["amount"] is None or value["currency"] is None:
            continue

        amount_usd = convert(value["amount"], value["currency"], "USD", rel_date)
        if amount_usd is None:
            continue

        amount_usd = int(amount_usd)

        if amount_usd >= 0:
            scope["prices"]["total_volume_positive"] += amount_usd
            scope["prices"]["contracts_positive"] += 1

            if 0 <= amount_usd <= 10000:
                scope["prices"]["price_category_positive"]["0_10000"]["volume"] += amount_usd
                scope["prices"]["price_category_positive"]["0_10000"]["contracts"] += 1
            elif 10001 <= amount_usd <= 100000:
                scope["prices"]["price_category_positive"]["10001_100000"]["volume"] += amount_usd
                scope["prices"]["price_category_positive"]["10001_100000"]["contracts"] += 1
            elif 100001 <= amount_usd <= 1000000:
                scope["prices"]["price_category_positive"]["100001_1000000"]["volume"] += amount_usd
                scope["prices"]["price_category_positive"]["100001_1000000"]["contracts"] += 1
            else:
                scope["prices"]["price_category_positive"]["1000001+"]["volume"] += amount_usd
                scope["prices"]["price_category_positive"]["1000001+"]["contracts"] += 1
        else:
            scope["prices"]["total_volume_negative"] += amount_usd
            scope["prices"]["contracts_negative"] += 1

    # period
    if rel_date:
        period = rel_date.replace(day=1)
        if period not in scope["_period_dict"]:
            scope["_period_dict"][period] = 1
        else:
            scope["_period_dict"][period] += 1

    return scope


def get_result(scope):
    # compiled releases
    scope["compiled_releases"]["total_unique_ocids"] = len(scope["compiled_releases"]["_ocid_set"])
    del scope["compiled_releases"]["_ocid_set"]

    # prices
    for key in scope["prices"]["price_category_positive"]:
        if scope["prices"]["total_volume_positive"] == 0:
            scope["prices"]["price_category_positive"][key]["share"] = 0
        else:
            scope["prices"]["price_category_positive"][key]["share"] = (
                scope["prices"]["price_category_positive"][key]["volume"] / scope["prices"]["total_volume_positive"]
            )

    # period
    min_date = min(scope["_period_dict"])
    max_date = max(scope["_period_dict"])

    scope["period"] = []
    current_date = min_date
    while current_date <= max_date:
        if current_date in scope["_period_dict"]:
            scope["period"].append(
                {"date_str": current_date.strftime(DATE_STR_FORMAT), "count": scope["_period_dict"][current_date]}
            )
        else:
            scope["period"].append({"date_str": current_date.strftime(DATE_STR_FORMAT), "count": 0})

        current_date += relativedelta(months=+1)

    del scope["_period_dict"]

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

    if result is None:
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
    with_collection = None
    package_data = None

    # with collection
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
        return meta_data

    with_collection = result

    kf_cursor.execute(
        "SELECT * FROM package_data WHERE id = %(id)s LIMIT 1",
        {"id": with_collection["package_data_id"]},
    )
    package_data = kf_cursor.fetchone()
    package_data = package_data if package_data else {}

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
    values = get_values(with_collection, "ocid", value_only=True)
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
