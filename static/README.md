# Static data README

This data is static, version-controlled data. To update it in prod, you must release a
new version of this repo and deploy the Docker image.

This data is "ingested" by copying it (and potentially also filtering it depending on
other data that comes in that day) during the ingest process.


## `common/`

### `colormaps.json`

These change rarely. They apply to both SSP and SWE data.


## `snow-surface-properties/`

### `variables.json`

These change rarely, but only because we enumerate every possible variable in this file.
The ingest process must filter down to only the variables available for that day, so the
webapp doesn't have to download all the "unreleased" variables that aren't ready yet.

> [!WARNING]
>
> The above paragraph actually lies a little bit; the `variables.json` file doesn't
> actually enumerate every possible variable _yet_. Sebastien is on it!


## `snow-water-equivalent/`

### `variables.json

Variable IDs must match column names coming from external provider.
