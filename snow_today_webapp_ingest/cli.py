"""CLI invoked by operations team.

NOTE: imports are done in functions to avoid needing to evaluate code within those
imports when doing `--help`.
"""
from datetime import date
from pathlib import Path
from tempfile import mkdtemp

import click
from click_loglevel import LogLevel
from loguru import logger

from snow_today_webapp_ingest.data_classes import VALIDATABLE_OUTPUT_DATA_CLASS_NAMES

# These aren't local imports because they're needed for a click decorator.
from snow_today_webapp_ingest.ingest.tasks import (
    ssp_ingest_tasks,
    swe_ingest_tasks,
)
from snow_today_webapp_ingest.types_.data_sources import DataSource

tasks_arg = click.argument(
    "tasks",
    type=click.Choice(tuple(ssp_ingest_tasks.keys())),
    nargs=-1,
)


@click.group()
@click.option(
    "-l",
    "--log-level",
    type=LogLevel(),
    default="DEBUG",
    help="Set logging level",
    show_default=True,
)
def cli(log_level: int) -> None:
    from snow_today_webapp_ingest.constants.paths import (
        STORAGE_DIR,
        storage_dir_default,
    )
    from snow_today_webapp_ingest.logging_ import setup_logger

    setup_logger(logger, log_level=log_level)

    if str(STORAGE_DIR) == storage_dir_default:
        logger.warning(
            f"$STORAGE_DIR envvar not set. Defaulting to output to '{STORAGE_DIR}'!"
        )
    pass


@cli.command()
@click.argument("schema", type=click.Choice(VALIDATABLE_OUTPUT_DATA_CLASS_NAMES))
def show_schema(schema) -> None:
    """Show SCHEMA in jsonschema format."""
    from snow_today_webapp_ingest.schema import get_jsonschema_str

    print(get_jsonschema_str(schema))


@cli.command()
# TODO: The idea of not taking a schema option isn't very sensible IMO; we can't always
#       rely on the filename to know what schema to use. We should get rid of it and
#       instead allow ingest functions to accept a callable that returns a path or
#       paths, or accept a regex as an optional kwarg.
@click.argument("file", type=click.Path(exists=True))
def validate_json(*, file: str) -> None:
    """Validate FILE (JSON) against given schema.

    TODO: Pass just filename and use pattern matching to detect the schema?
    """
    from snow_today_webapp_ingest.schema import validate_against_schema

    validate_against_schema(Path(file))
    logger.success("JSON is valid!")


# TODO: Add validate command to validate an output directory.


@cli.group()
@click.option(
    "--dry-run",
    is_flag=True,
    help=(
        "Do the ingest as normal, but skip moving the output to the final 'live'"
        " location."
    ),
)
@click.pass_context
def ingest(ctx, dry_run: bool) -> None:
    """Ingest data payload to update the webapp."""
    if dry_run:
        logger.warning("Starting dry-run; output will remain in WIP directory!")

    # Set up some context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj['dry_run'] = dry_run


@ingest.command()
@tasks_arg
@click.pass_context
def snow_surface_properties(ctx, *, tasks: tuple[str, ...]) -> None:
    """Run snow-surface-properties ingest tasks.

    If TASKS are passed, only run those.
    """
    _ingest(
        dry_run=ctx.obj["dry_run"],
        source="snow-surface-properties",
        tasks_include=tasks,
    )


@ingest.command()
@tasks_arg
@click.pass_context
def snow_water_equivalent(ctx, *, tasks: tuple[str, ...]) -> None:
    """Run snow-water-equivalent ingest tasks.

    If TASKS are passed, only run those.
    """
    _ingest(
        dry_run=ctx.obj["dry_run"],
        source="snow-water-equivalent",
        tasks_include=tasks,
    )


def _ingest(
    *,
    dry_run: bool,
    source: DataSource,
    tasks_include: tuple[str, ...],
) -> None:
    from snow_today_webapp_ingest.constants.paths import (
        INGEST_WIP_DIR,
        OUTPUT_BKP_DIR,
        OUTPUT_LIVE_SSP_DIR,
        OUTPUT_LIVE_SWE_DIR,
    )

    if source == "snow-surface-properties":
        task_set = ssp_ingest_tasks
        output_dir = OUTPUT_LIVE_SSP_DIR
    elif source == "snow-water-equivalent":
        task_set = swe_ingest_tasks
        output_dir = OUTPUT_LIVE_SWE_DIR
    else:
        # TODO: Can we get exhaustiveness checking from mypy somehow?
        raise RuntimeError("Programmer error.")

    if not tasks_include:
        # Run all the tasks
        tasks_to_run = task_set
    else:
        tasks_to_run = {
            key: value for key, value in task_set.items() if key in set(tasks_include)
        }

    tmpdir = Path(mkdtemp(dir=INGEST_WIP_DIR, prefix=f"{date.today()}_"))
    for ingest_task in tasks_to_run.values():
        ingest_task.ingest(ingest_tmpdir=tmpdir)

    if dry_run:
        logger.success(f"🎉 Ingested to '{tmpdir}'")
        logger.warning("This was a dry run; skipped moving data from WIP dir!")
        return

    bkp_dir = OUTPUT_BKP_DIR / source / f"bkp-{date.today()}"
    if output_dir.is_dir():
        # Do a swap: Live -> backup
        bkp_dir.parent.mkdir(parents=True, exist_ok=True)
        output_dir.rename(bkp_dir)
    else:
        # If it doesn't exist, we can't be sure its parents do:
        output_dir.parent.mkdir(parents=True, exist_ok=True)

    # Then another swap: New -> Live
    tmpdir.rename(output_dir)
    logger.success(f"🎉 Ingested to '{output_dir}'. Backup: '{bkp_dir}'")


if __name__ == '__main__':
    cli()
