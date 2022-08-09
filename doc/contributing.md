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

This repository contains the data needed to populate the `shapes/` directory. The
`cogs/` directory must be populated by running `scripts/make_cogs.sh` on GeoTIFFs
generated externally.
