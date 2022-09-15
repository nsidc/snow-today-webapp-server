import click

from make_cogs import make_cogs
from make_legends import make_legends
from make_plot_json import make_plot_json
from make_region_shapes_and_index import make_region_shapes_and_index


@click.group()
def cli():
    pass


@cli.command()
def make_cogs_daily():
    """Create Cloud-Optimized GeoTIFFs from GeoTIFFs on storage provider.

    Expected to run daily.
    """
    make_cogs()


@cli.command()
def make_plot_json_daily():
    """Create plot JSON from CSV on storage provider.

    Expected to run daily.
    """
    make_plot_json()


@cli.command(name='make-legends')
def make_legends_adhoc():
    """Create legends from `variables.json` data.

    Expected to run ad-hoc to create static legend files for new variables.
    """
    make_legends()


@cli.command(name='make-region-shapes-and-index')
def make_region_shapes_and_index_adhoc():
    """Create region GeoJSON files and regions.json index file from shapefiles.

    Shapefiles are found on storage provider.

    Expected to run ad-hoc to initialize new regions.
    """
    make_region_shapes_and_index()


if __name__ == '__main__':
    cli()
