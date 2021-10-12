#!/usr/bin/env python
import sys
from math import ceil

import click
import simplejson as json
from psycopg2 import sql

from core.state import phase, set_dataset_state, set_item_state, state
from settings.settings import get_param
from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor
from tools.logging_helper import get_logger
from tools.rabbit import ack, consume, publish

consume_routing_key = "_dataset_filter_extractor_init"
routing_key = "_extractor"
page_size = 1000
logger = None


@click.command()
@click.argument("environment")
def start(environment):
    init_worker(environment)
    consume(callback, get_param("exchange_name") + consume_routing_key)

    return


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
def callback(connection, channel, delivery_tag, body):
    cursor = get_cursor()
    try:
        input_message = json.loads(body.decode("utf8"))

        # checking input_message correctness
        if (
            "dataset_id_original" not in input_message
            or not isinstance(input_message["dataset_id_original"], int)
            or "filter_message" not in input_message
            or not isinstance(input_message["filter_message"], dict)
            or len(input_message["filter_message"]) == 0
        ):
            logger.warning("Input message is malformed, will be dropped.")
            ack(connection, channel, delivery_tag)
            return

        dataset_id_original = input_message["dataset_id_original"]
        filter_message = input_message["filter_message"]
        max_items = int(input_message["max_items"]) if "max_items" in input_message else None

        logger.info(
            "Checking whether dataset with dataset_id {} exists and can be filtered.".format(dataset_id_original)
        )
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
            );
            """,
            {"dataset_id": dataset_id_original},
        )
        if not cursor.fetchone()[0]:
            logger.warning(
                "Dataset with dataset_id {} does not exist or cannot be filtered.".format(dataset_id_original)
            )
            ack(connection, channel, delivery_tag)
            return

        logger.info("Creating row in dataset table for filtered dataset")
        cursor.execute(
            """
            INSERT INTO dataset
            (name, meta, ancestor_id)
            SELECT name, meta, null
            FROM dataset
            WHERE id = %s
            RETURNING id;
            """,
            (dataset_id_original,),
        )
        dataset_id_filtered = cursor.fetchone()[0]
        commit()

        logger.info("Creating row in dataset_filter table")
        cursor.execute(
            """
            INSERT INTO dataset_filter
            (dataset_id_original, dataset_id_filtered, filter_message)
            VALUES
            (%s, %s, %s);
            """,
            (dataset_id_original, dataset_id_filtered, json.dumps(filter_message)),
        )
        commit()

        logger.info("Filtering dataset with dataset_id {} using received filter_message".format(dataset_id_original))
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
        max_batch_size = get_param("extractor_max_batch_size")
        batch_size = 0
        batch = []

        i = 0
        items_inserted = 0
        items_count = len(ids)
        while i * page_size < items_count:
            page_ids = ids[i * page_size : (i + 1) * page_size]
            i = i + 1

            cursor.execute(
                """
                INSERT INTO data_item
                (data, dataset_id)
                SELECT data, %s
                FROM data_item
                WHERE id IN %s
                RETURNING id;
                """,
                (dataset_id_filtered, tuple(page_ids)),
            )
            commit()

            for row in cursor.fetchall():
                inserted_id = row[0]
                items_inserted = items_inserted + 1
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
                    message = {"item_ids": batch, "dataset_id": dataset_id_filtered}
                    publish(connection, channel, json.dumps(message), get_param("exchange_name") + routing_key)

                    batch_size = 0
                    batch.clear()

            logger.info(
                "Inserted page {} from {}. {} items out of {} downloaded".format(
                    i, ceil(float(items_count) / float(page_size)), items_inserted, items_count
                )
            )

        logger.info(
            "All original items with dataset_id {} have been duplicated with dataset_id {}".format(
                dataset_id_original, dataset_id_filtered
            )
        )

        ack(connection, channel, delivery_tag)

    except Exception:
        logger.exception("Something went wrong when processing {}".format(body))
        sys.exit()
    finally:
        cursor.close()


def init_worker(environment):
    bootstrap(environment, "dataset_filter_extractor")

    global logger
    logger = get_logger()

    logger.debug("Dataset filter extractor initialized.")


if __name__ == "__main__":
    start()
