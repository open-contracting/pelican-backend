#!/usr/bin/env python
import logging
from math import ceil

import click
import simplejson as json
from psycopg2 import sql
from yapw.methods.blocking import ack, publish

from tools import settings
from tools.services import commit, create_client, get_cursor
from tools.state import phase, set_dataset_state, set_item_state, state

consume_routing_key = "dataset_filter_extractor_init"
routing_key = "extractor"
page_size = 1000
logger = logging.getLogger("pelican.workers.extract.dataset_filter")


@click.command()
def start():
    """
    Add filtered datasets.
    """
    create_client().consume(callback, consume_routing_key)


# input message example
# {
#     "dataset_id_original": 2,
#     "filter_message": {
#         "release_date_from": '2019-12-02',
#         "release_date_to": '2020-02-02',
#         "buyer": ["ministry_of_finance", "state"],
#         "buyer_regex": "Development$",
#         "procuring_entity": ["a", "b"],
#         "procuring_entity_regex": "(a|b)casdf+"

#     },
#     "max_items": 5000
# }
def callback(client_state, channel, method, properties, input_message):
    delivery_tag = method.delivery_tag
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
            logger.warning("Input message is malformed, will be dropped.")
            ack(client_state, channel, delivery_tag)
            return

        dataset_id_original = input_message["dataset_id_original"]
        filter_message = input_message["filter_message"]
        max_items = int(input_message["max_items"]) if "max_items" in input_message else None

        logger.info("Checking whether dataset with dataset_id %s exists and can be filtered.", dataset_id_original)
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM dataset
                WHERE id = %(dataset_id)s
            )
            AND EXISTS (
                SELECT 1
                FROM progress_monitor_dataset
                WHERE dataset_id = %(dataset_id)s
                AND phase = 'CHECKED'
            )
            """,
            {"dataset_id": dataset_id_original},
        )
        if not cursor.fetchone()[0]:
            logger.warning("Dataset with dataset_id %s does not exist or cannot be filtered.", dataset_id_original)
            ack(client_state, channel, delivery_tag)
            return

        logger.info("Creating row in dataset table for filtered dataset")
        cursor.execute(
            """
            INSERT INTO dataset (name, meta, ancestor_id)
            SELECT name, meta, NULL FROM dataset WHERE id = %(ancestor_id)s
            RETURNING id
            """,
            {"ancestor_id": dataset_id_original},
        )
        dataset_id_filtered = cursor.fetchone()[0]
        commit()

        logger.info("Creating row in dataset_filter table")
        cursor.execute(
            """
            INSERT INTO dataset_filter (dataset_id_original, dataset_id_filtered, filter_message)
            VALUES (%(dataset_id_original)s, %(dataset_id_filtered)s, %(filter_message)s)
            """,
            {
                "dataset_id_original": dataset_id_original,
                "dataset_id_filtered": dataset_id_filtered,
                "filter_message": json.dumps(filter_message),
            },
        )
        commit()

        logger.info("Filtering dataset with dataset_id %s using received filter_message", dataset_id_original)
        query = sql.SQL("SELECT id FROM data_item WHERE dataset_id = ") + sql.Literal(dataset_id_original)
        if "release_date_from" in filter_message:
            expr = sql.SQL("data->>'date' >= ") + sql.Literal(filter_message["release_date_from"])
            query += sql.SQL(" and ") + expr
        if "release_date_to" in filter_message:
            expr = sql.SQL("data->>'date' <= ") + sql.Literal(filter_message["release_date_to"])
            query += sql.SQL(" and ") + expr
        if "buyer" in filter_message:
            expr = sql.SQL(", ").join([sql.Literal(buyer) for buyer in filter_message["buyer"]])
            expr = sql.SQL("data->'buyer'->>'name' in ") + sql.SQL("(") + expr + sql.SQL(")")
            query += sql.SQL(" and ") + expr
        if "buyer_regex" in filter_message:
            expr = sql.SQL("data->'buyer'->>'name' ilike ") + sql.Literal(filter_message["buyer_regex"])
            query += sql.SQL(" and ") + expr
        if "procuring_entity" in filter_message:
            expr = sql.SQL(", ").join(
                [sql.Literal(procuring_entity) for procuring_entity in filter_message["procuring_entity"]]
            )
            expr = sql.SQL("data->'tender'->'procuringEntity'->>'name' in ") + sql.SQL("(") + expr + sql.SQL(")")
            query += sql.SQL(" and ") + expr
        if "procuring_entity_regex" in filter_message:
            expr = sql.SQL("data->'tender'->'procuringEntity'->>'name' ilike ") + sql.Literal(
                filter_message["procuring_entity_regex"]
            )
            query += sql.SQL(" and ") + expr
        if max_items is not None:
            query += sql.SQL(" LIMIT ") + sql.Literal(max_items)
        query += sql.SQL(";")

        logger.info(query.as_string(cursor))

        cursor.execute(query)
        ids = [row[0] for row in cursor.fetchall()]

        # batch initialization
        max_batch_size = settings.EXTRACTOR_MAX_BATCH_SIZE
        batch_size = 0
        batch = []

        i = 0
        items_inserted = 0
        items_count = len(ids)
        while i * page_size < items_count:
            page_ids = ids[i * page_size : (i + 1) * page_size]
            i += 1

            cursor.execute(
                """
                INSERT INTO data_item (data, dataset_id)
                SELECT data, %(dataset_id)s FROM data_item WHERE id IN %(ids)s
                RETURNING id
                """,
                {"dataset_id": dataset_id_filtered, "ids": tuple(page_ids)},
            )
            commit()

            for row in cursor.fetchall():
                inserted_id = row[0]
                items_inserted += 1
                set_item_state(dataset_id_filtered, inserted_id, state.IN_PROGRESS)
                set_dataset_state(
                    dataset_id_filtered, state.IN_PROGRESS, phase.CONTRACTING_PROCESS, size=items_inserted
                )
                if items_inserted == items_count:
                    set_dataset_state(dataset_id_filtered, state.OK, phase.CONTRACTING_PROCESS)
                commit()

                batch_size += 1
                batch.append(inserted_id)
                if batch_size >= max_batch_size or items_inserted == items_count:
                    publish(client_state, channel, {"item_ids": batch, "dataset_id": dataset_id_filtered}, routing_key)

                    batch_size = 0
                    batch.clear()

            logger.info(
                "Inserted page %s from %s. %s items out of %s downloaded",
                i,
                ceil(float(items_count) / float(page_size)),
                items_inserted,
                items_count,
            )

        logger.info(
            "All original items with dataset_id %s have been duplicated with dataset_id %s",
            dataset_id_original,
            dataset_id_filtered,
        )

        ack(client_state, channel, delivery_tag)
    finally:
        cursor.close()


if __name__ == "__main__":
    start()
