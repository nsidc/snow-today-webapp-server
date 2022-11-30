# Contributing

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
