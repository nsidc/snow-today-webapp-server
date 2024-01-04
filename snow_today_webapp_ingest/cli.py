"""CLI invoked by operations team.

NOTE: imports are done in functions to avoid needing to evaluate code within those
imports when doing `--help`.
"""
from datetime import date
from pathlib import Path
from tempfile import mkdtemp

import click
from loguru import logger

# This isn't a local import because it's needed for a click decorator.
from snow_today_webapp_ingest.ingest.tasks import ingest_tasks


@click.group()
def cli() -> None:
    pass


@cli.group()
def ingest() -> None:
    pass


@ingest.command()
@click.option(
    "--dry-run",
    default=False,
    help=(
        "Do the ingest as normal, but skip moving the output to the final 'live'"
        " location."
    ),
)
@click.argument(
    "tasks",
    type=click.Choice(tuple(ingest_tasks.keys())),
    nargs=-1,
)
def snow_surface_properties(*, tasks: tuple[str, ...], dry_run: bool) -> None:
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

    if dry_run:
        logger.info(f"🎉 Successfully ingested to '{tmpdir}'")
        logger.warning("NOTE: This was a dry run, so the data remains in the WIP dir!")
        return

    bkp_dir = OUTPUT_LIVE_DIR.parent / f"bkp-{date.today()}"

    OUTPUT_LIVE_DIR.rename(bkp_dir)
    tmpdir.rename(OUTPUT_LIVE_DIR)
    logger.info(
        f"🎉 Successfully ingested to '{OUTPUT_LIVE_DIR}'." f" Backup: '{bkp_dir}'"
    )


@ingest.command()
def snow_water_equivalent() -> None:
    """Run daily snow-water equivalent ingest."""
    try:
        from snow_today_webapp_ingest.make_swe_json import make_swe_json

        make_swe_json()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e


if __name__ == '__main__':
    cli()
