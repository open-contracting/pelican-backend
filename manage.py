#!/usr/bin/env python
import click

from pelican.util import exchange_rates_db, settings
from pelican.util.services import Phase, State, commit, get_cursor, publish, update_dataset_state


@click.group()
def cli():
    pass


@cli.command()
def update_exchange_rates():
    """Update the exchange rates."""
    if settings.FIXER_IO_API_KEY:
        exchange_rates_db.update_from_fixer_io()


@cli.command()
@click.argument("name")
@click.argument("collection_id", type=int)
@click.option("--previous-dataset", type=int, help="ID of previous dataset for time-based checks.")
@click.option("--sample", type=int, help="Number of compiled releases to import.")
def add(name, collection_id, previous_dataset, sample):
    """Create a dataset."""
    message = {"name": name, "collection_id": collection_id, "ancestor_id": previous_dataset, "max_items": sample}
    publish(message, "ocds_kingfisher_extractor_init")


@cli.command()
@click.argument("dataset_id", type=int)
@click.option("--include-filtered", is_flag=True, help="Remove its filtered datasets.")
@click.option("--force", is_flag=True, help="Forcefully remove the dataset.")
def remove(dataset_id, include_filtered, force):
    """Delete a dataset."""
    cursor = get_cursor()

    cursor.execute("SELECT EXISTS (SELECT 1 FROM dataset WHERE id = %(id)s)", {"id": dataset_id})
    if not cursor.fetchone()[0]:
        click.secho(f"Dataset {dataset_id} doesn't exist.", err=True, fg="red")
        return

    cursor.execute(
        "SELECT phase, state FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s",
        {"dataset_id": dataset_id},
    )
    row = cursor.fetchone()
    if not row or row[0] not in {Phase.CHECKED, Phase.DELETED} or row[1] != State.OK:
        if force:
            click.secho(
                f"Forcefully removing dataset {dataset_id} (phase={row[0]}, state={row[1]}). (Its phase should be "
                f"{Phase.CHECKED} or {Phase.DELETED}, and its state should be {State.OK}.)",
                fg="yellow",
                err=True,
            )
        else:
            click.secho(
                f"Dataset {dataset_id} (phase={row[0]}, state={row[1]}) can't be removed. Its phase must be "
                f"{Phase.CHECKED} or {Phase.DELETED}, and its state must be {State.OK}.",
                fg="red",
                err=True,
            )
            return

    delete_dataset_ids = [dataset_id]
    if include_filtered:
        while True:
            cursor.execute(
                """\
                SELECT p.dataset_id
                FROM progress_monitor_dataset p
                WHERE
                    p.phase = ANY(%(phases)s)
                    AND p.state = %(state)s
                    AND EXISTS (
                        SELECT 1
                        FROM dataset_filter
                        WHERE
                            dataset_id_original = ANY(%(dataset_ids)s)
                            AND dataset_id_filtered = p.dataset_id
                    )
                """,
                {
                    "phases": [Phase.CHECKED, Phase.DELETED],
                    "state": State.OK,
                    "dataset_ids": delete_dataset_ids,
                },
            )
            new_delete_dataset_ids = [row[0] for row in cursor] + [dataset_id]
            if sorted(delete_dataset_ids) == sorted(new_delete_dataset_ids):
                break

            delete_dataset_ids = new_delete_dataset_ids.copy()

    click.echo(f"Removing dataset(s) {', '.join(map(str, delete_dataset_ids))}... ", nl=False)

    parameters = {"dataset_ids": delete_dataset_ids}
    cursor.execute("DELETE FROM field_level_check             WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM field_level_check_examples    WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM resource_level_check          WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM resource_level_check_examples WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM report                        WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM dataset_level_check           WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM time_variance_level_check     WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM progress_monitor_item         WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute("DELETE FROM data_item                     WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    cursor.execute(
        """\
        UPDATE progress_monitor_dataset
        SET phase = %(phase)s, state = %(state)s, modified = now()
        WHERE dataset_id = ANY(%(dataset_ids)s)
        """,
        {
            "dataset_ids": delete_dataset_ids,
            "phase": Phase.DELETED,
            "state": State.OK,
        },
    )

    commit()
    click.echo("done")

    click.echo("Checking if rows can be deleted in dataset, dataset_filter, progress_monitor_dataset...")
    drop_dataset_ids = []
    while True:
        cursor.execute(
            """\
            SELECT p.dataset_id
            FROM progress_monitor_dataset p
            WHERE
                p.phase = %(phase)s
                AND p.state = %(state)s
                AND NOT EXISTS (
                    SELECT 1
                    FROM dataset_filter
                    WHERE
                        dataset_id_original = p.dataset_id
                        AND dataset_id_filtered <> ALL(%(dataset_ids)s)
                )
            """,
            {
                "phase": Phase.DELETED,
                "state": State.OK,
                "dataset_ids": drop_dataset_ids,
            },
        )
        new_drop_dataset_ids = [row[0] for row in cursor]
        if sorted(drop_dataset_ids) == sorted(new_drop_dataset_ids):
            break

        drop_dataset_ids = new_drop_dataset_ids.copy()

    if drop_dataset_ids:
        click.echo(f"Purging dataset(s) {', '.join(map(str, drop_dataset_ids))}... ", nl=False)

        parameters = {"dataset_ids": drop_dataset_ids}
        cursor.execute("DELETE FROM progress_monitor_dataset WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
        cursor.execute(
            """\
            DELETE FROM dataset_filter
            WHERE dataset_id_original = ANY(%(dataset_ids)s) OR dataset_id_filtered = ANY(%(dataset_ids)s)
            """,
            parameters,
        )
        cursor.execute("DELETE FROM dataset WHERE id = ANY(%(dataset_ids)s)", parameters)

        commit()
        click.echo("done")

    cursor.close()


@cli.group()
def dev():
    """Commands for administrators and developers of Pelican backend."""


@dev.command()
@click.argument("dataset_id", type=int)
def restart_dataset_check(dataset_id):
    """Restart the dataset check if the check.dataset worker failed."""
    update_dataset_state(dataset_id, Phase.CONTRACTING_PROCESS, State.OK)
    commit()

    message = {"dataset_id": dataset_id}
    publish(message, "contracting_process_checker")


if __name__ == "__main__":
    cli()
