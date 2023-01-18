#!/usr/bin/env python
import click
import psycopg2.extras
import simplejson as json

import dataset.meta_data_aggregator as meta_data_aggregator
from tools import exchange_rates_db, settings
from tools.services import commit, consume, get_cursor
from tools.workers import process_items

consume_routing_key = "ocds_kingfisher_extractor_init"
routing_key = "extractor"


@click.command()
def start():
    """
    Import collections from Kingfisher Process.
    """
    consume(callback, consume_routing_key)


def callback(client_state, channel, method, properties, input_message):
    if settings.FIXER_IO_API_KEY:
        exchange_rates_db.update_from_fixer_io()

    cursor = get_cursor()
    kf_connection = psycopg2.connect(settings.KINGFISHER_PROCESS_DATABASE_URL)
    kf_cursor = kf_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        name = input_message["name"]
        collection_id = input_message["collection_id"]
        max_items = input_message["max_items"]
        ancestor_id = input_message["ancestor_id"]

        if max_items is None:
            kf_cursor.execute(
                """\
                SELECT compiled_release.data_id
                FROM compiled_release
                JOIN data ON compiled_release.data_id = data.id
                WHERE
                    compiled_release.collection_id = %(collection_id)s
                    AND pg_column_size(data.data) < %(max_size)s
                """,
                {"collection_id": collection_id, "max_size": settings.KINGFISHER_PROCESS_MAX_SIZE},
            )
        else:
            kf_cursor.execute(
                """\
                SELECT compiled_release.data_id
                FROM compiled_release
                JOIN data ON compiled_release.data_id = data.id
                WHERE
                    compiled_release.collection_id = %(collection_id)s
                    AND pg_column_size(data.data) < %(max_size)s
                LIMIT %(limit)s
                """,
                {"collection_id": collection_id, "max_size": settings.KINGFISHER_PROCESS_MAX_SIZE, "limit": max_items},
            )

        ids = [row[0] for row in kf_cursor.fetchall()]

        cursor.execute(
            """\
            INSERT INTO dataset (name, meta, ancestor_id)
            VALUES (%(name)s, %(meta)s, %(ancestor_id)s)
            RETURNING id
            """,
            {"name": name, "meta": json.dumps({}), "ancestor_id": ancestor_id},
        )
        dataset_id = cursor.fetchone()[0]

        meta_data = meta_data_aggregator.get_kingfisher_meta_data(collection_id)
        meta_data_aggregator.update_meta_data(meta_data, dataset_id)

        commit()

        process_items(
            client_state=client_state,
            channel=channel,
            method=method,
            routing_key=routing_key,
            cursors={"default": cursor, "kingfisher_process": kf_cursor},
            dataset_id=dataset_id,
            ids=ids,
            insert_data_items=insert_data_items,
        )
    finally:
        kf_cursor.close()
        kf_connection.close()
        cursor.close()


def insert_data_items(cursors, dataset_id, ids):
    cursors["kingfisher_process"].execute("SELECT data FROM data WHERE data.id IN %(ids)s", {"ids": tuple(ids)})
    data_items = [(json.dumps(row[0]), dataset_id) for row in cursors["kingfisher_process"].fetchall()]
    sql = "INSERT INTO data_item (data, dataset_id) VALUES %s RETURNING id"
    psycopg2.extras.execute_values(cursors["default"], sql, data_items, page_size=settings.EXTRACTOR_PAGE_SIZE)


if __name__ == "__main__":
    start()
