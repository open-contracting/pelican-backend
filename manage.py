#!/usr/bin/env python3
import functools
from pathlib import Path

import click
import requests

from contracting_process.field_level.definitions import coverage_checks
from contracting_process.field_level.definitions import definitions as field_level
from contracting_process.resource_level.definitions import definitions as resource_level
from dataset.definitions import definitions as dataset_level
from pelican.util import codelists, exchange_rates_db, settings
from pelican.util.services import Phase, State, commit, execute, publish, update_dataset_state
from time_variance.definitions import definitions as time_level

# updatedocs command
MESSAGES_URL = "https://raw.githubusercontent.com/open-contracting/pelican-frontend/main/frontend/src/messages/{}.json"
DESCRIPTION_KEYS = ("descriptionLong", "description")
DEFAULT_LOCALE = "en"
# The headings aren't in Pelican frontend, which uses different wording in its user interface.
CHECKS_PAGES = {
    "en": {
        "title": "Quality checks",
        "sections": {
            "field": "Field-level",
            "resourceLevel": "Compiled release-level",
            "datasetLevel": "Dataset-level",
            "timeLevel": "Time-based",
        },
        "categories": {
            "coverage": "Coverage",
            "quality": "Quality",
            "coherent": "Coherence",
            "consistent": "Consistency",
            "reference": "Reference",
            "distribution": "Distribution",
            "misc": "Miscellaneous",
            "unique": "Uniqueness",
        },
    },
    "es": {
        "title": "Verificaciones de calidad",
        "sections": {
            "field": "A nivel de campo",
            "resourceLevel": "A nivel de compiled release",
            "datasetLevel": "A nivel de dataset",
            "timeLevel": "Basadas en el tiempo",
        },
        "categories": {
            "coverage": "Cobertura",
            "quality": "Calidad",
            "coherent": "Coherencia",
            "consistent": "Consistencia",
            "reference": "Referencia",
            "distribution": "Distribución",
            "misc": "Misceláneo",
            "unique": "Unicidad",
        },
    },
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


def markdown_heading(text, level):
    return [f"{'#' * level} {text}", ""]


def markdown_paragraphs(html):
    # "{'$'}" escapes a dollar sign in a Vue I18n message.
    return [html.replace("{'$'}", "$"), ""]


def markdown_checks(messages, level):
    """Return the Markdown for each check's name and description, and the checks' identifiers."""
    content = []
    identifiers = set()
    for identifier, check in messages.items():
        if isinstance(check, dict) and "name" in check:
            content.extend(markdown_heading(check["name"], level))
            content.extend(markdown_paragraphs(next(check[key] for key in DESCRIPTION_KEYS if key in check)))
            identifiers.add(identifier)
    return content, identifiers


def markdown_category(messages, categories):
    """Return the Markdown for the checks in each category, and the checks' identifiers."""
    content = []
    identifiers = set()
    for category, checks in messages.items():
        if category in categories:
            lines, keys = markdown_checks(checks, 4)
            content.extend(markdown_heading(categories[category], 3))
            content.extend(lines)
            identifiers |= {f"{category}.{key}" for key in keys}
    return content, identifiers


def markdown_page(locale, page):
    """Return the Markdown for the locale's docs page."""
    messages = get_messages(DEFAULT_LOCALE)
    if locale != DEFAULT_LOCALE:
        messages = merge_messages(messages, get_messages(locale))

    sections = page["sections"]
    markdown_categories = functools.partial(markdown_category, categories=page["categories"])

    field_identifiers = {f"coverage.{name}" for _, name in coverage_checks} | {
        f"quality.{name}" for checks in field_level.values() for _, name in checks
    }

    content = ["% Generated by: ./manage.py dev updatedocs", "", *markdown_heading(page["title"], 1)]

    for section_key, function, checks_key, defined in (
        ("field", markdown_categories, "fieldDetail", field_identifiers),
        ("resourceLevel", markdown_categories, "resourceLevel", set(resource_level)),
        ("datasetLevel", markdown_categories, "datasetLevel", set(dataset_level)),
        ("timeLevel", functools.partial(markdown_checks, level=3), "timeLevel", set(time_level)),
    ):
        lines, documented = function(messages[checks_key])
        content.extend(markdown_heading(sections[section_key], 2))
        content.extend(markdown_paragraphs(messages[section_key]["description"]))
        content.extend(lines)
        if locale == DEFAULT_LOCALE:
            compare(sections[section_key], defined, documented)

    return "\n".join(content)


@functools.cache
def get_messages(locale):
    response = requests.get(MESSAGES_URL.format(locale), timeout=10)
    response.raise_for_status()
    return response.json()


def merge_messages(messages, translations):
    """Merge the translations into the default locale's messages, like Vue I18n's fallback."""
    merged = messages.copy()
    for key, value in translations.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_messages(merged[key], value)
        else:
            merged[key] = value
    return merged


def compare(title, defined, documented):
    for repository, identifiers in (("frontend", defined - documented), ("backend", documented - defined)):
        if identifiers:
            click.secho(f"{title} checks not in Pelican {repository}: {', '.join(identifiers)}", fg="yellow", err=True)


@dev.command()
def updatedocs():
    """Update the docs/checks pages, using the checks' names and descriptions from Pelican frontend."""
    directory = Path(__file__).resolve().parent / "docs" / "checks"
    for locale, page in CHECKS_PAGES.items():
        (directory / f"{locale}.md").write_text(markdown_page(locale, page))


@dev.command()
def updatecodelists():
    """Update the OCDS codelist files in the pelican/static/codelists directory."""
    for name, url in codelists.CODELIST_URLS.items():
        response = codelists.session.get(url, timeout=10)
        response.raise_for_status()
        (codelists.CODELIST_DIR / name).write_bytes(response.content)


if __name__ == "__main__":
    cli()
