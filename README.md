# Snow Today Webapp Server

Serve data supporting the [Snow Today
Webapp](https://github.com/nsidc/snow-today-webapp). This data is version-controlled in
this repository, with the exception of Cloud Optimized GeoTIFFs and plot data, which are
populated dynamically on a daily basis.

[More on data served by Snow Today Webapp Server](doc/data.md)


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
docker-compose build
```


## Usage

```
docker-compose up
```


## Troubleshooting

*TODO*


## License

See [LICENSE](LICENSE).


## Contributing

See [contributing docs](doc/contributing.md).
