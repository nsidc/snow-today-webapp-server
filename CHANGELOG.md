# v0.16.0 (2022-12-13)

* Tweak text for Normalized SWE legend and longname


# v0.15.0 (2022-12-07)

* Change SWE delta longname and legend text


# v0.14.0 (2022-12-07)

* Add SWE variables to `variables.json` and redefined the `type` attribute for all
  entries
* Generate static SWE legends
* Change `notprocessed` colormap to yellow to match other graphics


# v0.13.1 (2022-12-01)

* Bugfix: Add `./data` directory to ingest docker image


# v0.13.0 (2022-11-29)

* Migrate existing daily ingest task to `ingest-daily-ssp`
* Add `ingest-daily-swe` command to create Snow-Water Equivalent JSON files from
  incoming CSV.


# v0.12.0 (2022-09-20)

* Add `make-dynamic-legends-daily` ops command: Generates legends which have dynamic
  colormap value ranges specified by variable name `$DOWY` in config.


# v0.11.2 (2022-09-17)

* Fixup docker-compose configuration to pass needed environment variables


# v0.11.1 (2022-09-16)

* Fixup deploy and CLI script to not clobber images or leave ended ingest containers
  behind.


# v0.11.0 (2022-09-16)

* Initial release of versioned ingest code and Docker image.


# v0.10.1 (2022-09-15)

* Fix configured precision for Snow Cover Days variable


# v0.10.0 (2022-09-15)

* Add variable parameters to `variables.json`:
  * `precision`: Number of digits to the right of decimal point
  * `longname_plot`: The alternate variable longname displayed for plots


# v0.9.0 (2022-09-15)

* Calculate legend "extend" parameter dynamically based on `value_range` in
  `variables.json`.
* Generate SVGs in a more deterministic manner to minimize superfluous differences.


# v0.8.0 (2022-09-14)

* Recreate legends as SVG
* Update legend appearance to be smaller overall (including font)


# v0.7.1 (2022-09-13)

* Fixup legend labels


# v0.7.0 (2022-09-13)

* Add legends images and update `variables.json` with paths to legends


# v0.6.0 (2022-09-12)

* Solidify the variable `type` field as `enum: ["variable", "notprocessed"]`


# v0.5.0 (2022-09-12)

* Update albedo NODATA value -> 255


# v0.4.1 (2022-09-12)

* Move `notprocessed` var to end of variables index.


# v0.4.0 (2022-09-06)

* Support "default" and "enabled" parameters for variables.


# v0.3.0 (2022-08-24)

* Support a 1-level region hierarchy. Each region can have many sub-region collections,
  each containing many sub-regions.


# v0.2.1 (2022-08-22)

* Fix deploy script docker-compose invocation


# v0.2.0 (2022-08-22)

* Add "US West complete" region


# v0.1.2 (2022-08-22)

* Fixup deployment script typo


# v0.1.1 (2022-08-19)

* Add deployment script


# v0.1.0 (2022-08-18)

* Initial version
