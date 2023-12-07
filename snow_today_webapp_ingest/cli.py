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
def cli():
    pass


@cli.command()
def make_cogs_daily():
    """Create Cloud-Optimized GeoTIFFs from GeoTIFFs on storage provider.

    Expected to run daily.
    """
    try:
        from snow_today_webapp_ingest.make_cogs import make_cogs

        make_cogs()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e


@cli.command()
def make_plot_json_daily():
    """Create plot JSON from CSV on storage provider.

    Expected to run daily.
    """
    try:
        from snow_today_webapp_ingest.make_plot_json import make_plot_json

        make_plot_json()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e


@cli.command()
def make_dynamic_legends_daily():
    """Create daily dynamic legend image(s) from `variables.json data.

    Expected to run daily.

    Dynamic legends are recognized by presence of an expected string variablename, e.g.
    `$DOWY`, in the `colormap_value_range` entry.
    """
    try:
        from snow_today_webapp_ingest.make_dynamic_legends import make_dynamic_legends

        make_dynamic_legends()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e


@cli.command()
@click.pass_context
def ingest_daily_ssp(ctx):
    """Run all daily snow surface properties ingest tasks."""
    ctx.invoke(make_cogs_daily)
    ctx.invoke(make_plot_json_daily)
    ctx.invoke(make_dynamic_legends_daily)
    # ctx.invoke(make_metadata_daily)


@cli.command()
def ingest_daily_swe():
    """Run daily snow-water equivalent ingest."""
    try:
        from snow_today_webapp_ingest.make_swe_json import make_swe_json

        make_swe_json()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e


@cli.command(name='make-static-legends')
def make_static_legends_adhoc():
    """Create static legend image(s) from `variables.json` data.

    Expected to run ad-hoc to create static legend files for new or changed variables.
    """
    try:
        from snow_today_webapp_ingest.make_static_legends import make_static_legends

        make_static_legends()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e


@cli.command(name='make-region-shapes-and-index')
def make_region_shapes_and_index_adhoc():
    """Create region GeoJSON files and regions.json index file from shapefiles.

    Shapefiles are found on storage provider.

    Expected to run ad-hoc to initialize new regions.

    TODO: How to only _update_ instead of fully recreating?
    """
    try:
        from snow_today_webapp_ingest.make_region_shapes_and_index import (
            make_region_shapes_and_index,
        )

        make_region_shapes_and_index()
    except Exception as e:
        logger.exception(e)
        raise click.ClickException(str(e)) from e


@cli.command()
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
    type=click.Choice(ingest_tasks.keys()),
    nargs=-1,
)
def new_ingest(*, tasks: tuple[str], dry_run: bool) -> None:
    """Run all ingest tasks. If TASKS is provided, run those only."""
    from snow_today_webapp_ingest.constants.paths import INGEST_WIP_DIR, OUTPUT_LIVE_DIR

    tmpdir = mkdtemp(dir=INGEST_WIP_DIR, prefix=f"{date.today()}_")

    if not tasks:
        # Run all the tasks
        tasks_to_run = ingest_tasks
    else:
        tasks_to_run = {
            key: value for key, value in ingest_tasks.items() if key in set(tasks)
        }

    for ingest_task in tasks_to_run.values():
        ingest_task.run(ingest_tmpdir=Path(tmpdir))

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


if __name__ == '__main__':
    cli()
