#!/usr/bin/env python
import logging

import click

from tools import exchange_rates_db, settings
from tools.db import commit, get_cursor
from tools.rabbit import create_client
from tools.state import phase, state


@click.group()
def cli():
    pass


@cli.command()
def update_exchange_rates():
    """
    Update the exchange rates.
    """
    if settings.FIXER_IO_API_KEY:
        exchange_rates_db.update_from_fixer_io()


@cli.command()
@click.argument("name")
@click.argument("collection_id")
@click.option("--previous-dataset", type=int, help="ID of previous dataset for time-based checks.")
@click.option("--sample", type=int, help="Number of compiled releases to import.")
def add(name, collection_id, previous_dataset, sample):
    """
    Create a dataset.
    """
    message = {"name": name, "collection_id": collection_id, "ancestor_id": previous_dataset, "max_items": sample}
    create_client().publish(message, "ocds_kingfisher_extractor_init")


@cli.command()
@click.argument("dataset_id", type=int)
@click.option("--include-filtered", is_flag=True, help="Delete its filtered datasets.")
def remove(dataset_id, filtered):
    """
    Delete a dataset.
    """
    logger = logging.getLogger("pelican.remove")

    cursor = get_cursor()

    # checking if dataset exists
    cursor.execute("SELECT EXISTS (SELECT 1 FROM dataset WHERE id = %(id)s)", {"id", dataset_id})
    if not cursor.fetchone()[0]:
        logger.error("Dataset with dataset_id %s does not exist.", dataset_id)
        return

    cursor.execute("SELECT phase, state FROM progress_monitor_dataset WHERE dataset_id = %(id)s", {"id": dataset_id})
    row = cursor.fetchone()
    if not row or row[0] not in (phase.CHECKED, phase.DELETED) or row[1] != state.OK:
        logger.error(
            "Dataset with dataset_id %s cannot be deleted. "
            "For a successful deletion the dataset should be in '%s' or '%s' phase and '%s' state.",
            dataset_id,
            phase.CHECKED,
            phase.DELETED,
            state.OK,
        )
        return

    # searching for descendant filtered datasets
    delete_dataset_ids = [dataset_id]
    if filtered:
        while True:
            cursor.execute(
                """
                    SELECT p.dataset_id
                    FROM progress_monitor_dataset p
                    WHERE p.phase IN %(phases)s AND p.state = %(state)s AND EXISTS (
                        SELECT 1
                        FROM dataset_filter
                        WHERE dataset_id_original IN %(dataset_ids)s AND dataset_id_filtered = p.dataset_id
                    )
                """,
                {
                    "phases": (phase.CHECKED, phase.DELETED),
                    "state": state.OK,
                    "dataset_ids": tuple(delete_dataset_ids),
                },
            )
            new_delete_dataset_ids = [row[0] for row in cursor.fetchall()] + [dataset_id]
            if sorted(delete_dataset_ids) == sorted(new_delete_dataset_ids):
                break

            delete_dataset_ids = new_delete_dataset_ids.copy()

    # safely deleting dataset
    logger.info(
        "Deleting datasets with the following dataset_ids: %s. "
        "Only rows in the following tables will remain: dataset, dataset_filter, progress_monitor_dataset.",
        delete_dataset_ids,
    )
    cursor.execute(
        """
        DELETE FROM field_level_check WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM field_level_check_examples WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM resource_level_check WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM resource_level_check_examples WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM report WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM dataset_level_check WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM time_variance_level_check WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM progress_monitor_item WHERE dataset_id IN %(dataset_ids)s;
        DELETE FROM data_item WHERE dataset_id IN %(dataset_ids)s;

        UPDATE progress_monitor_dataset
        SET phase = %(phase)s, state = %(state)s, modified = NOW()
        WHERE dataset_id IN %(dataset_ids)s;
        """,
        {
            "dataset_ids": tuple(delete_dataset_ids),
            "phase": phase.DELETED,
            "state": state.OK,
        },
    )
    commit()

    logger.info("Datasets with dataset_ids %s have been deleted.", delete_dataset_ids)

    # dropping datasets if no dependencies exist
    logger.info("Checking if some deleted datasets can be dropped entirely.")
    drop_dataset_ids = []
    while True:
        cursor.execute(
            """
                SELECT p.dataset_id
                FROM progress_monitor_dataset p
                WHERE p.phase = %(phase)s AND p.state = %(state)s AND NOT EXISTS (
                    SELECT 1
                    FROM dataset_filter
                    WHERE dataset_id_original = p.dataset_id AND NOT dataset_id_filtered IN %(dataset_ids)s
                )
            """,
            {
                "phase": phase.DELETED,
                "state": state.OK,
                "dataset_ids": tuple(drop_dataset_ids + [-1]),
            },
        )
        new_drop_dataset_ids = [row[0] for row in cursor.fetchall()]
        if sorted(drop_dataset_ids) == sorted(new_drop_dataset_ids):
            break

        drop_dataset_ids = new_drop_dataset_ids.copy()

    if drop_dataset_ids:
        logger.info("The following datasets will be dropped entirely: %s", drop_dataset_ids)
        cursor.execute(
            """
                DELETE FROM dataset WHERE id IN %(dataset_ids)s;

                DELETE FROM dataset_filter
                WHERE dataset_id_original IN %(dataset_ids)s OR dataset_id_filtered IN %(dataset_ids)s;

                DELETE FROM progress_monitor_dataset WHERE dataset_id IN %(dataset_ids)s;
            """,
            {"dataset_ids": tuple(drop_dataset_ids)},
        )
        commit()

    cursor.close()
    logger.info("Successful deletion executed.")


if __name__ == "__main__":
    cli()
