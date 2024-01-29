"""CLI invoked by operations team.

NOTE: imports are done in functions to avoid needing to evaluate code within those
imports when doing `--help`.
"""
from pathlib import Path
from tempfile import mkdtemp

import click
from click_loglevel import LogLevel
from loguru import logger

# NOTE: These aren't local imports because they're needed for a click decorator or
# shared between functions.
from snow_today_webapp_ingest.constants.date import TODAY
from snow_today_webapp_ingest.data_classes import (
    SSP_OUTPUT_DATA_CLASS_NAMES,
    SSP_OUTPUT_DATA_CLASSES,
    SWE_OUTPUT_DATA_CLASS_NAMES,
    SWE_OUTPUT_DATA_CLASSES,
    OutputDataClass,
)
from snow_today_webapp_ingest.types_.data_sources import DataSource

swe_tasks_arg = click.argument(
    "swe_tasks",
    type=click.Choice(tuple(SWE_OUTPUT_DATA_CLASS_NAMES)),
    nargs=-1,
)
ssp_tasks_arg = click.argument(
    "ssp_tasks",
    type=click.Choice(tuple(SSP_OUTPUT_DATA_CLASS_NAMES)),
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


# TODO: Restore these commands by creating a collection of top-level models, i.e. the
#       ones used in docs, and allowing those as choices for printing jsonschema.
#       Validate would take that argument plus the file to validate.
#
# @cli.command()
# @click.argument("schema", type=click.Choice(VALIDATABLE_OUTPUT_DATA_CLASS_NAMES))
# def show_schema(schema) -> None:
#     """Show SCHEMA in jsonschema format."""
#     from snow_today_webapp_ingest.schema import get_jsonschema_str
#
#     print(get_jsonschema_str(schema))
#
#
# @cli.command()
# # TODO: The idea of not taking a schema option isn't very sensible IMO; we can't
# # always rely on the filename to know what schema to use. We should get rid of it and
# # instead allow ingest functions to accept a callable that returns a path or paths, or
# # accept a regex as an optional kwarg.
# @click.argument("file", type=click.Path(exists=True))
# def validate_json(*, file: str) -> None:
#     """Validate FILE (JSON) against given schema.
#
#     TODO: Pass just filename and use pattern matching to detect the schema?
#     """
#     from snow_today_webapp_ingest.schema import validate_against_schema
#
#     validate_against_schema(Path(file))
#     logger.success("JSON is valid!")

# TODO: Add command to validate an output directory.


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
@ssp_tasks_arg
@click.pass_context
def snow_surface_properties(ctx, *, ssp_tasks: tuple[str, ...]) -> None:
    """Run snow-surface-properties ingest tasks.

    If TASKS are passed, only run those.
    """
    _ingest(
        dry_run=ctx.obj["dry_run"],
        source="snow-surface-properties",
        tasks_include=ssp_tasks,
    )


@ingest.command()
@swe_tasks_arg
@click.pass_context
def snow_water_equivalent(ctx, *, swe_tasks: tuple[str, ...]) -> None:
    """Run snow-water-equivalent ingest tasks.

    If TASKS are passed, only run those.
    """
    _ingest(
        dry_run=ctx.obj["dry_run"],
        source="snow-water-equivalent",
        tasks_include=swe_tasks,
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

    # TODO: This should be a mapping:
    if source == "snow-surface-properties":
        data_class_set = SSP_OUTPUT_DATA_CLASSES
        output_dir = OUTPUT_LIVE_SSP_DIR
    elif source == "snow-water-equivalent":
        data_class_set = SWE_OUTPUT_DATA_CLASSES
        output_dir = OUTPUT_LIVE_SWE_DIR
    else:
        # TODO: Can we get exhaustiveness checking from mypy?
        raise RuntimeError("Programmer error.")

    tasks_to_run: list[OutputDataClass]
    if not tasks_include:
        # Run all the tasks
        tasks_to_run = list(data_class_set.values())
    else:
        tasks_to_run = [
            dc
            for dc_name, dc in data_class_set.items()
            if dc_name in set(tasks_include)
        ]

    tmpdir = Path(mkdtemp(dir=INGEST_WIP_DIR, prefix=f"{TODAY}_"))
    # NOTE: mkdtemp always creates directories with 0700. Therefore:
    tmpdir.chmod(0o755)

    for ingest_task in tasks_to_run:
        ingest_task.ingest(ingest_tmpdir=tmpdir)

    if dry_run or tasks_include:
        desc = "dry" if dry_run else "partial"
        logger.success(f"🎉 Ingested to '{tmpdir}'")
        logger.warning(f"This was a {desc} run; skipped moving data from WIP dir!")
        logger.warning(
            "If you wish to use this data in production, you must copy it manually"
            " or re-run this program with neither a task filter nor dry run flag."
        )
        return

    bkp_dir = _unique_backup_dir(OUTPUT_BKP_DIR / source)
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


def _unique_backup_dir(parent: Path) -> Path:
    """Generate a backup directory path that doesn't conflict.

    In case multiple runs are taken in a single day, we don't want the program to fail
    creating a backup dir.
    """
    dirname = f"bkp-{TODAY}"
    path = parent / dirname

    counter = 1
    while path.is_dir():
        path = parent / f"{dirname}_{counter}"
        counter = counter + 1

    return path


if __name__ == '__main__':
    cli()
