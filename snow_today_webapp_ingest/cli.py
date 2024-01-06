"""CLI invoked by operations team.

NOTE: imports are done in functions to avoid needing to evaluate code within those
imports when doing `--help`.
"""
import sys
from datetime import date
from pathlib import Path
from tempfile import mkdtemp

import click
from click_loglevel import LogLevel
from loguru import logger

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
def cli(log_level: LogLevel) -> None:
    from snow_today_webapp_ingest.constants.paths import (
        STORAGE_DIR,
        storage_dir_default,
    )

    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.level("INFO", color="<white>")

    if str(STORAGE_DIR) == storage_dir_default:
        logger.warning(
            f"$STORAGE_DIR envvar not set. Defaulting to output to '{STORAGE_DIR}'!"
        )
    pass


# TODO: Add validate command to validate an output directory.


@cli.group(help="Ingest data payload to update the webapp")
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
        ingest_task.run(ingest_tmpdir=tmpdir)

    if dry_run:
        logger.success(f"🎉 Ingested to '{tmpdir}'")
        logger.warning("This was a dry run; skipped moving data from WIP dir!")
        return

    # Do a swap: Live -> backup; new -> live
    bkp_dir = OUTPUT_BKP_DIR / source / f"bkp-{date.today()}"
    output_dir.rename(bkp_dir)
    tmpdir.rename(output_dir)
    logger.success(f"🎉 Ingested to '{output_dir}'. Backup: '{bkp_dir}'")


if __name__ == '__main__':
    cli()
