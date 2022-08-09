# Contributing

## Data structure

Data lives in `data/` directory. Some of it is provided by this repo, and some is
generated dynamically.

```
cogs/                   # Cloud-Optimized GeoTIFFs of raster data variables
  ...
shapes/                 # Shapes of various regions/sub-regions
  states/
    index.json
    <region_id>.json 
statistics/             # Statistics for generating plot visualizations
  ...
```

This repository contains the data needed to populate the `shapes/` directory. The
`cogs/` directory must be populated by running `scripts/make_cogs.sh` on GeoTIFFs
generated externally.

TODO: Statistics...
