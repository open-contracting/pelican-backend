#!/usr/bin/env python3
import functools
from pathlib import Path

import click
import requests

from pelican.util import exchange_rates_db, settings
from pelican.util.services import Phase, State, commit, execute, publish, update_dataset_state

CATEGORIES = {
    "coverage": "Coverage",
    "quality": "Quality",
    "coherent": "Coherence",
    "consistent": "Consistency",
    "reference": "Reference",
    "distribution": "Distribution",
    "misc": "Miscellaneous",
    "unique": "Uniqueness",
}


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
    row = execute("SELECT EXISTS (SELECT 1 FROM dataset WHERE id = %(id)s) AS exists", {"id": dataset_id}).fetchone()
    if not row["exists"]:
        click.secho(f"Dataset {dataset_id} doesn't exist.", err=True, fg="red")
        return

    row = execute(
        "SELECT phase, state FROM progress_monitor_dataset WHERE dataset_id = %(dataset_id)s",
        {"dataset_id": dataset_id},
    ).fetchone()
    if not row or row["phase"] not in {Phase.CHECKED, Phase.DELETED} or row["state"] != State.OK:
        if force:
            click.secho(
                f"Forcefully removing dataset {dataset_id} (phase={row['phase']}, state={row['state']}). (Its phase "
                f"should be {Phase.CHECKED} or {Phase.DELETED}, and its state should be {State.OK}.)",
                fg="yellow",
                err=True,
            )
        else:
            click.secho(
                f"Dataset {dataset_id} (phase={row['phase']}, state={row['state']}) can't be removed. Its phase "
                f"must be {Phase.CHECKED} or {Phase.DELETED}, and its state must be {State.OK}.",
                fg="red",
                err=True,
            )
            return

    delete_dataset_ids = [dataset_id]
    if include_filtered:
        while True:
            rows = execute(
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
            new_delete_dataset_ids = [row["dataset_id"] for row in rows] + [dataset_id]
            if sorted(delete_dataset_ids) == sorted(new_delete_dataset_ids):
                break

            delete_dataset_ids = new_delete_dataset_ids.copy()

    click.echo(f"Removing dataset(s) {', '.join(map(str, delete_dataset_ids))}... ", nl=False)

    parameters = {"dataset_ids": delete_dataset_ids}
    execute("DELETE FROM field_level_check             WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM field_level_check_examples    WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM resource_level_check          WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM resource_level_check_examples WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM report                        WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM dataset_level_check           WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM time_variance_level_check     WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM progress_monitor_item         WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute("DELETE FROM data_item                     WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
    execute(
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
        rows = execute(
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
        new_drop_dataset_ids = [row["dataset_id"] for row in rows]
        if sorted(drop_dataset_ids) == sorted(new_drop_dataset_ids):
            break

        drop_dataset_ids = new_drop_dataset_ids.copy()

    if drop_dataset_ids:
        click.echo(f"Purging dataset(s) {', '.join(map(str, drop_dataset_ids))}... ", nl=False)

        parameters = {"dataset_ids": drop_dataset_ids}
        execute("DELETE FROM progress_monitor_dataset WHERE dataset_id = ANY(%(dataset_ids)s)", parameters)
        execute(
            """\
            DELETE FROM dataset_filter
            WHERE dataset_id_original = ANY(%(dataset_ids)s) OR dataset_id_filtered = ANY(%(dataset_ids)s)
            """,
            parameters,
        )
        execute("DELETE FROM dataset WHERE id = ANY(%(dataset_ids)s)", parameters)

        commit()
        click.echo("done")


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


DESCRIPTION_KEYS = ("descriptionLong", "description_long", "description", "count_header_tooltip")


def markdown_heading(text, level):
    return [f"{'#' * level} {text}", ""]


def markdown_paragraphs(html):
    # "{'$'}" escapes a dollar sign in a Vue I18n message.
    return [html.replace("{'$'}", "$"), ""]


def markdown_checks(messages, name_key, level):
    """Return the Markdown for each check's name and description, and the checks' identifiers."""
    content = []
    identifiers = set()
    for identifier, check in messages.items():
        if isinstance(check, dict) and name_key in check:
            content.extend(markdown_heading(check[name_key], level))
            content.extend(markdown_paragraphs(next(check[key] for key in DESCRIPTION_KEYS if key in check)))
            identifiers.add(identifier)
    return content, identifiers


def markdown_category(messages, name_key):
    """Return the Markdown for the checks in each category, and the checks' identifiers."""
    content = []
    identifiers = set()
    for category, checks in messages.items():
        if category in CATEGORIES:
            lines, keys = markdown_checks(checks, name_key, 4)
            content.extend(markdown_heading(CATEGORIES[category], 3))
            content.extend(lines)
            identifiers |= {f"{category}.{key}" for key in keys}
    return content, identifiers


def compare(title, defined, documented):
    for repository, identifiers in (("frontend", defined - documented), ("backend", documented - defined)):
        if identifiers:
            click.secho(f"{title} checks not in Pelican {repository}: {', '.join(identifiers)}", fg="yellow", err=True)


@dev.command()
def updatedocs():
    """Update the docs/checks.md page, using the check names and descriptions from Pelican frontend."""
    import json5  # a development requirement, only

    from contracting_process.field_level.definitions import coverage_checks
    from contracting_process.field_level.definitions import definitions as field_level
    from contracting_process.resource_level.definitions import definitions as resource_level
    from dataset.definitions import definitions as dataset_level
    from time_variance.definitions import definitions as time_level

    messages_url = (
        "https://raw.githubusercontent.com/open-contracting/pelican-frontend/main/frontend/src/messages/en.js"
    )
    response = requests.get(messages_url, timeout=10)
    response.raise_for_status()
    # Remove the "export const messages = " prefix and the ";" suffix.
    messages = json5.loads(response.text.split("=", 1)[1].strip().rstrip(";"))

    field_identifiers = {f"coverage.{name}" for _, name in coverage_checks} | {
        f"quality.{name}" for checks in field_level.values() for _, name in checks
    }

    content = ["% Generated by: ./manage.py dev updatedocs", "", *markdown_heading("Quality checks", 1)]

    for title, description_key, function, checks_key, name_key, defined in (
        ("Field-level", "field", markdown_category, "fieldDetail", "count_header", field_identifiers),
        ("Compiled release-level", "resourceLevel", markdown_category, "resourceLevel", "name", set(resource_level)),
        ("Dataset-level", "datasetLevel", markdown_category, "datasetLevel", "name", set(dataset_level)),
        ("Time-based", "timeLevel", functools.partial(markdown_checks, level=3), "timeLevel", "name", set(time_level)),
    ):
        lines, documented = function(messages[checks_key], name_key)
        content.extend(markdown_heading(title, 2))
        content.extend(markdown_paragraphs(messages[description_key]["description"]))
        content.extend(lines)
        compare(title, defined, documented)

    (Path(__file__).resolve().parent / "docs" / "checks.md").write_text("\n".join(content))


if __name__ == "__main__":
    cli()
