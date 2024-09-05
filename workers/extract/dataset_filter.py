import logging

import click
from psycopg2 import sql
from yapw.methods import nack

from pelican.util.services import Json, commit, consume, get_cursor
from pelican.util.workers import process_items

consume_routing_key = "dataset_filter_extractor_init"
routing_key = "extractor"
logger = logging.getLogger("pelican.workers.extract.dataset_filter")


@click.command()
def start():
    """
    Create filtered datasets.
    """
    consume(on_message_callback=callback, queue=consume_routing_key)


# Sample message:
# > {
# >     "dataset_id_original": 2,
# >     "filter_message": {
# >         "release_date_from": '2019-12-02',
# >         "release_date_to": '2020-02-02',
# >         "buyer": ["ministry_of_finance", "state"],
# >         "buyer_regex": "Development$",
# >         "procuring_entity": ["a", "b"],
# >         "procuring_entity_regex": "(a|b)casdf+"
# >     },
# >     "max_items": 5000
# > }
def callback(client_state, channel, method, properties, input_message):
    cursor = get_cursor()

    try:
        # checking input_message correctness
        if (
            "dataset_id_original" not in input_message
            or not isinstance(input_message["dataset_id_original"], int)
            or "filter_message" not in input_message
            or not isinstance(input_message["filter_message"], dict)
            or len(input_message["filter_message"]) == 0
        ):
            logger.error("Message is malformed, skipping (%r)", input_message)
            nack(client_state, channel, method.delivery_tag, requeue=False)
            return

        dataset_id_original = input_message["dataset_id_original"]
        filter_message = input_message["filter_message"]
        max_items = input_message.get("max_items")

        cursor.execute(
            """\
            SELECT meta
            FROM dataset
            JOIN progress_monitor_dataset ON dataset_id = dataset.id
            WHERE
                dataset.id = %(dataset_id)s
                AND phase = 'CHECKED'
            """,
            {"dataset_id": dataset_id_original},
        )
        row = cursor.fetchone()
        if not row:
            logger.error("No dataset in phase CHECKED with id %s, skipping", dataset_id_original)
            nack(client_state, channel, method.delivery_tag, requeue=False)
            return

        meta = {
            k: v
            for k, v in row[0].items()
            if k not in {"tender_lifecycle", "compiled_releases", "data_quality_tool_metadata"}
        }

        cursor.execute(
            """\
            INSERT INTO dataset (name, meta, ancestor_id)
            SELECT name, %(meta)s, NULL FROM dataset WHERE id = %(dataset_id)s
            RETURNING id
            """,
            {"dataset_id": dataset_id_original, "meta": Json(meta)},
        )
        dataset_id_filtered = cursor.fetchone()[0]
        commit()

        cursor.execute(
            """\
            INSERT INTO dataset_filter (dataset_id_original, dataset_id_filtered, filter_message)
            VALUES (%(dataset_id_original)s, %(dataset_id_filtered)s, %(filter_message)s)
            """,
            {
                "dataset_id_original": dataset_id_original,
                "dataset_id_filtered": dataset_id_filtered,
                "filter_message": Json(filter_message),
            },
        )
        commit()

        variables = {"dataset_id_original": dataset_id_original}
        parts = ["SELECT id FROM data_item WHERE dataset_id = %(dataset_id_original)s"]

        if "release_date_from" in filter_message:
            variables["release_date_from"] = filter_message["release_date_from"]
            parts.append("AND data->>'date' >= %(release_date_from)s")

        if "release_date_to" in filter_message:
            variables["release_date_to"] = filter_message["release_date_to"]
            parts.append("AND data->>'date' <= %(release_date_to)s")

        if "buyer" in filter_message:
            variables["buyer"] = tuple(filter_message["buyer"])
            parts.append("AND data->'buyer'->>'name' IN %(buyer)s")

        if "buyer_regex" in filter_message:
            variables["buyer_regex"] = filter_message["buyer_regex"]
            parts.append("AND data->'buyer'->>'name' ILIKE %(buyer_regex)s")

        if "procuring_entity" in filter_message:
            variables["procuring_entity"] = tuple(filter_message["procuring_entity"])
            parts.append("AND data->'tender'->'procuringEntity'->>'name' IN %(procuring_entity)s")

        if "procuring_entity_regex" in filter_message:
            variables["procuring_entity_regex"] = filter_message["procuring_entity_regex"]
            parts.append("AND data->'tender'->'procuringEntity'->>'name' ILIKE %(procuring_entity_regex)s")

        if max_items is not None:
            variables["limit"] = max_items
            parts.append("LIMIT %(limit)s")

        statement = sql.SQL(" ".join(parts))
        logger.info(statement.as_string(cursor))

        cursor.execute(statement, variables)
        ids = [row[0] for row in cursor]

        process_items(
            client_state=client_state,
            channel=channel,
            method=method,
            routing_key=routing_key,
            cursors={"default": cursor},
            dataset_id=dataset_id_filtered,
            ids=ids,
            insert_items=insert_items,
        )
    finally:
        cursor.close()


def insert_items(cursors, dataset_id, ids):
    cursors["default"].execute(
        """\
        INSERT INTO data_item (data, dataset_id)
        SELECT data, %(dataset_id)s FROM data_item WHERE id = ANY(%(ids)s)
        RETURNING id
        """,
        {"dataset_id": dataset_id, "ids": ids},
    )


if __name__ == "__main__":
    start()
