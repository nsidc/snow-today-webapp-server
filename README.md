[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/nsidc/snow-today-webapp-server/main.svg)](https://results.pre-commit.ci/latest/github/nsidc/snow-today-webapp-server/main)

# Snow Today Webapp Server

Generate and serve data supporting the [Snow Today
Webapp](https://github.com/nsidc/snow-today-webapp).

Static data is version-controlled in this repository. Daily dynamic data (e.g.
Cloud-Optimized GeoTIFFs) are generated by executing code in this repository.

[More on data served by Snow Today Webapp Server](doc/data.md)

NOTE: Because there is a co-dependency between the dynamic data-generation code and the
static configuration code, they are intentionally versioned together in this repository.


## Level of Support

This repository is not actively supported by NSIDC but we welcome issue submissions and
pull requests in order to foster community contribution.

See the [LICENSE](LICENSE) for details on permissions and warranties. Please contact
nsidc@nsidc.org for more information.


## Requirements

This package requires a webserver to host its data, as well as GDAL for
creating Cloud-Optimized GeoTIFFs.


## Installation

```
docker compose build
```


## Usage

Ensure envvars `$ENVIRONMENT` and `$STORAGE_DIR` are set appropriately, e.g.:

```
export ENVIRONMENT=dev  # default: production
export STORAGE_DIR=/tmp/snow-today-data
```

`STORAGE_DIR` is expected to contain an `incoming` subdirectory where daily data will
arrive, and `cogs` and `plots` directories, where outputs will be written.


### Start the data server

```
docker compose up -d data-server
```

### Ingest data

```
./scripts/container_cli.sh --help
./scripts/container_cli.sh make-cogs-daily
./scripts/container_cli.sh make-plot-json-daily
```


## Troubleshooting

### Webserver `403` errors

Permissions on a directory are not set correctly. Need `ugo+rx`. In an NSIDC deployment,
an operator can correct this on the storage back-end.


## License

See [LICENSE](LICENSE).


## Contributing

See [contributing docs](doc/contributing.md).
