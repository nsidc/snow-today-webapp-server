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

from snow_today_webapp_ingest.constants.paths import STORAGE_DIR, storage_dir_default

# This isn't a local import because it's needed for a click decorator.
from snow_today_webapp_ingest.ingest.tasks import ingest_tasks


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
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.level("INFO", color="<white>")

    if str(STORAGE_DIR) == storage_dir_default:
        logger.warning(
            f"$STORAGE_DIR envvar not set. Defaulting to output to '{STORAGE_DIR}'!"
        )
    pass


@cli.group(help="Ingest daily payload from the supercomputer to update the webapp")
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
    ctx.ensure_object(dict)
    ctx.obj['dry_run'] = dry_run

    if dry_run:
        logger.warning("Starting dry-run; output will remain in WIP directory!")


@ingest.command()
@click.argument(
    "tasks",
    type=click.Choice(tuple(ingest_tasks.keys())),
    nargs=-1,
)
@click.pass_context
def snow_surface_properties(ctx, *, tasks: tuple[str, ...]) -> None:
    """Run snow-surface-properties ingest tasks, default to all tasks.

    If TASKS is provided, run those only.
    """
    from snow_today_webapp_ingest.constants.paths import INGEST_WIP_DIR, OUTPUT_LIVE_DIR

    tmpdir = Path(mkdtemp(dir=INGEST_WIP_DIR, prefix=f"{date.today()}_"))

    if not tasks:
        # Run all the tasks
        tasks_to_run = ingest_tasks
    else:
        tasks_to_run = {
            key: value for key, value in ingest_tasks.items() if key in set(tasks)
        }

    for ingest_task in tasks_to_run.values():
        ingest_task.run(ingest_tmpdir=tmpdir)

    if ctx.obj["dry_run"]:
        logger.success(f"🎉 Ingested to '{tmpdir}'")
        logger.warning("This was a dry run; skipped moving data from WIP dir!")
        return

    bkp_dir = OUTPUT_LIVE_DIR.parent / f"bkp-{date.today()}"

    OUTPUT_LIVE_DIR.rename(bkp_dir)
    tmpdir.rename(OUTPUT_LIVE_DIR)
    logger.success(f"🎉 Ingested to '{OUTPUT_LIVE_DIR}'. Backup: '{bkp_dir}'")


@ingest.command()
@click.pass_context
def snow_water_equivalent(ctx) -> None:
    """Run daily snow-water equivalent ingest."""
    try:
        from snow_today_webapp_ingest.make_swe_json import make_swe_json

        make_swe_json()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e

    if ctx.obj["dry_run"]:
        logger.warning("This was a dry run; skipped moving data from WIP dir!")


if __name__ == '__main__':
    cli()
