#!/usr/bin/env python
import os
import shutil
import tempfile
import time

import click
import requests
import shortuuid
import simplejson as json

from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor
from tools.logging_helper import get_logger
from tools.rabbit import connect_and_publish_message
from tools.state import phase, state


@click.group()
def cli():
    pass


@cli.command()
@click.argument("name")
@click.argument("collection_id")
@click.option("--previous-dataset", type=int, help="ID of previous dataset for time-based checks.")
@click.option("--sample", type=int, help="Number of compiled releases to import.")
def add(name, collection_id, previous_dataset, sample):
    """
    Create a dataset.
    """
    bootstrap("pelican.add")

    global logger
    logger = get_logger()

    logger.info("Updating registries...")
    with open(os.path.join("pelican", "static", "origin.json"), "r") as json_file:
        origin = json.load(json_file)

    for path, urls in origin.items():
        logger.info("Updating registry on path %s" % path)
        update_registry(path, urls)

    routing_key = "ocds_kingfisher_extractor_init"

    message = {
        "name": name,
        "collection_id": collection_id,
        "ancestor_id": previous_dataset,
        "max_items": sample,
    }
    connect_and_publish_message(json.dumps(message), routing_key)


def update_registry(path, urls, file_format="csv"):
    tempdir = tempfile.mkdtemp()
    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            logger.warning("File at %s could not be downloaded" % url)
            continue

        with open(os.path.join(tempdir, shortuuid.uuid()), "wb") as file:
            file.write(response.content)

        logger.info("File at %s was successfully downloaded; sleeping for 2 seconds" % url)
        time.sleep(2)

    logger.info("Joining all the files...")
    if file_format == "csv":
        with open(path, "w") as registry_file:
            for index, file_name in enumerate(os.listdir(tempdir)):
                with open(os.path.join(tempdir, file_name), "r") as file:
                    if index != 0:
                        file.__next__()
                    for line in file:
                        registry_file.write(line)
    else:
        shutil.rmtree(tempdir)
        raise ValueError("File format '%s' is not supported" % file_format)

    shutil.rmtree(tempdir)


@cli.command()
@click.argument("dataset_id", type=int)
@click.option("--include-filtered", is_flag=True, help="Delete its filtered datasets.")
def remove(dataset_id, filtered):
    """
    Delete a dataset.
    """
    bootstrap("pelican.remove")

    global logger
    logger = get_logger()

    cursor = get_cursor()

    logger.info("Script initialized")

    # checking if dataset exists
    cursor.execute(
        """
        select exists (
            select 1
            from dataset
            where id = %s
        );
        """,
        (dataset_id,),
    )
    if not cursor.fetchall()[0][0]:
        logger.error("Dataset with dataset_id %s does not exist." % dataset_id)
        return

    # checking if dataset can be deleted
    cursor.execute(
        """
        select phase, state
        from progress_monitor_dataset
        where dataset_id = %s;
        """,
        (dataset_id,),
    )
    rows = cursor.fetchall()
    if not rows or rows[0][0] not in (phase.CHECKED, phase.DELETED) or rows[0][1] != state.OK:
        logger.error(
            (
                "Dataset with dataset_id %s cannot be deleted. "
                "For a successful deletion the dataset should be in '%s' or '%s' phase and '%s' state."
            )
            % (dataset_id, phase.CHECKED, phase.DELETED, state.OK)
        )
        return

    # searching for descendant filtered datasets
    delete_dataset_ids = [dataset_id]
    if filtered:
        while True:
            cursor.execute(
                """
                select p.dataset_id
                from progress_monitor_dataset as p
                where p.phase in %(phases)s and
                    p.state = %(state)s and
                    exists (
                        select 1
                        from dataset_filter
                        where dataset_id_original in %(dataset_ids)s and
                            dataset_id_filtered = p.dataset_id
                    );
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
        (
            "Deleting datasets with the following dataset_ids: %s. "
            "Only rows in the following tables will remain: dataset, dataset_filter, progress_monitor_dataset."
        )
        % str(delete_dataset_ids)
    )
    cursor.execute(
        """
        delete from report
        where dataset_id in %(dataset_ids)s;

        delete from progress_monitor_item
        where dataset_id in %(dataset_ids)s;

        delete from data_item
        where dataset_id in %(dataset_ids)s;

        delete from field_level_check
        where dataset_id in %(dataset_ids)s;

        delete from field_level_check_examples
        where dataset_id in %(dataset_ids)s;

        delete from resource_level_check
        where dataset_id in %(dataset_ids)s;

        delete from resource_level_check_examples
        where dataset_id in %(dataset_ids)s;

        delete from dataset_level_check
        where dataset_id in %(dataset_ids)s;

        delete from time_variance_level_check
        where dataset_id in %(dataset_ids)s;

        update progress_monitor_dataset
        set phase = %(phase)s, state = %(state)s, modified = now()
        where dataset_id in %(dataset_ids)s;
        """,
        {
            "dataset_ids": tuple(delete_dataset_ids),
            "phase": phase.DELETED,
            "state": state.OK,
        },
    )
    commit()

    logger.info("Datasets with dataset_ids %s have been deleted." % str(delete_dataset_ids))

    # dropping datasets if no dependencies exist
    logger.info("Checking if some deleted datasets can be dropped entirely.")
    drop_dataset_ids = []
    while True:
        cursor.execute(
            """
            select p.dataset_id
            from progress_monitor_dataset as p
            where p.phase = %(phase)s and
                p.state = %(state)s and
                not exists (
                    select 1
                    from dataset_filter
                    where dataset_id_original = p.dataset_id and
                        not dataset_id_filtered in %(dataset_ids)s
                );
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
        logger.info("The following datasets will be dropped entirely: %s" % str(drop_dataset_ids))
        cursor.execute(
            """
            delete from dataset
            where id in %(dataset_ids)s;

            delete from dataset_filter
            where dataset_id_original in %(dataset_ids)s or
                dataset_id_filtered in %(dataset_ids)s;

            delete from progress_monitor_dataset
            where dataset_id in %(dataset_ids)s;
            """,
            {"dataset_ids": tuple(drop_dataset_ids)},
        )
        commit()

    cursor.close()
    logger.info("Successful deletion executed.")


if __name__ == "__main__":
    cli()