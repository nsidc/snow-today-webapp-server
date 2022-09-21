"""CLI invoked by operations team.

NOTE: imports are done in functions to avoid needing to evaluate code within those
imports when doing `--help`.
"""
import click


@click.group()
def cli():
    pass


@cli.command()
def make_cogs_daily():
    """Create Cloud-Optimized GeoTIFFs from GeoTIFFs on storage provider.

    Expected to run daily.
    """
    from make_cogs import make_cogs
    make_cogs()


@cli.command()
def make_plot_json_daily():
    """Create plot JSON from CSV on storage provider.

    Expected to run daily.
    """
    from make_plot_json import make_plot_json
    make_plot_json()
    

@cli.command()
def make_dynamic_legends_daily():
    """Create daily dynamic legend image(s) from `variables.json data.

    Expected to run daily.

    Dynamic legends are recognized by presence of an expected string variablename, e.g.
    `$DOWY`, in the `colormap_value_range` entry.
    """
    from make_dynamic_legends import make_dynamic_legends
    make_dynamic_legends()


@cli.command()
def make_metadata_daily():
    """Create `today.json` with details about the current set of data."""
    # { curren_dowy: ..., ...?} 
    ...


@cli.command()
@click.pass_context
def ingest_daily(ctx):
    """Run all daily ingest tasks."""
    ctx.invoke(make_cogs_daily)
    ctx.invoke(make_plot_json_daily)
    ctx.invoke(make_dynamic_legends_daily)
    ctx.invoke(make_metadata_daily)


@cli.command(name='make-static-legends')
def make_static_legends_adhoc():
    """Create static legend image(s) from `variables.json` data.

    Expected to run ad-hoc to create static legend files for new or changed variables.
    """
    from make_static_legends import make_static_legends
    make_static_legends()


@cli.command(name='make-region-shapes-and-index')
def make_region_shapes_and_index_adhoc():
    """Create region GeoJSON files and regions.json index file from shapefiles.

    Shapefiles are found on storage provider.

    Expected to run ad-hoc to initialize new regions.

    TODO: How to only _update_ instead of fully recreating?
    """
    from make_region_shapes_and_index import make_region_shapes_and_index
    make_region_shapes_and_index()


if __name__ == '__main__':
    cli()
