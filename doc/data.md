# Data served by this app

## Static, versioned data managed by this repo

* `variables.json`: Index of available variables. Maintained by hand.
* `regions.json`: Index of available regions and their associated subregion collections.
  Produced by `scripts/make_region_shapes_and_index.py`, but hand-editing is expected
  after initial creation.
* `shapes/*.geojson`: Shapes (GeoJSON) of each region. Produced by
  `scripts/make_region_shapes_and_index.py`.


## Dynamic data produced on a daily basis

These data are produced daily on the Research Computing hardware, transferred to NSIDC
hardware, and post-processed for use by the webapp.

* `cogs/`: Cloud-Optimized GeoTIFFs. ~9 per day (1 for each variable). These are
  originally created on RC as regular GeoTIFFs, transferred, then post-processed by
  `scripts/make_cogs.sh` to produce final COGs.
* `plots/`: JSON data series for plotting. Each file contains keys: `day_of_water_year`,
  `min`, `max`, `prc25`, `prc75`, `median`, and `year_to_date`. These are originally
  created on RC as CSV files, transferred, then post-processed by
  `scripts/make_plot_json.py` to produce final JSON.
