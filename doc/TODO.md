# Data structure

* Split `variables.json` to `variables/raster.json` and `variables/swe.json`?

# Code organization

* How should the daily data ingest functionality and the static data be related?
  * Currently they live in the same repo and their version numbers are in lockstep.
    Consequences include: Building ingest image when only changing dynamic data and
    vice versa. Benefits include: No need to think about compatibility between static
    data versions and ingest versions.


# Data validation

* Schemas
* Validate relationships between json files


# Python tooling

* Static analysis (lint/typecheck) in CI
* A unified CLI interface for operational tooling?


# Deployment / release tooling

* Build static content into a versioned Dockerfile?
