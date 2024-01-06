# Data served by this app

:::{.callout-warning}
This page is out of date.

_TODO: Update!_
:::


## Static, versioned data managed by this repo

This data will be baked into the `snow-today-webapp-server` Docker image.

* `variables.json`: Index of available variables. Maintained by hand.
* `regions.json`: Index of available regions and their associated subregion collections.
  Produced by `make_region_shapes_and_index.py`, but hand-editing is expected
  after initial creation.
* `shapes/*.geojson`: Shapes (GeoJSON) of each region. Produced by
  `make_region_shapes_and_index.py`.


## Dynamic data produced on a daily basis

These data are produced daily on the Research Computing hardware, transferred to NSIDC
hardware, and post-processed for use by the webapp.

This data is expected to be mounted at runtime.

* `cogs/`: Cloud-Optimized GeoTIFFs. ~9 per day (1 for each variable). These are
  originally created on RC as regular GeoTIFFs, transferred, then post-processed by
  `make_cogs.sh` to produce final COGs.
* `plots/`: JSON data series for plotting. Each file contains keys: `day_of_water_year`,
  `min`, `max`, `prc25`, `prc75`, `median`, and `year_to_date`. These are originally
  created on RC as CSV files, transferred, then post-processed by
  `make_plot_json.py` to produce final JSON.


## Data structure

Data lives in `data/` directory. Some of it is provided by this repo, and some is
generated dynamically.

```
variables.json        # Index of available variables and expected COG location
cogs/                 # Cloud-Optimized GeoTIFFs of raster data variables
  <variable>.tif      # A .tif for each indexed variable must exist
shapes/               # Shapes of various regions/sub-regions
  states/
    index.json        # Index of available regions
    <region_id>.json  # A .json for each indexed region must exist
statistics/           # Statistics for generating plot visualizations
  ...                 # TODO...
```

This repository contains the data needed to populate the index files and the `shapes/`
directory.

The `cogs/` directory must be populated by running `make-cogs-daily` on GeoTIFFs generated
externally.


## Data validation

GeoJSON can be validated with `jsonschema`, installed via `conda env create`.


## Data processing

The `make-cogs-daily` script for processing external GeoTIFFs into app-ready COGs requires
GDAL. It can be installed with `conda env create`.
