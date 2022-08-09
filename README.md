# Snow Today Webapp Server

Serve data supporting the Snow Today Webapp. This data is version-controlled in
this repository, with the exception of Cloud Optimized GeoTIFFs, which are
populated dynamically on a daily basis.

* Index of available variables
* Cloud-Optimized GeoTIFFs for each variable (populated dynamically)
* Index of available regions and subregions
* Shapes (GeoJSON) of each region


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
