## 2023

- [ ] Write to a temporary output location and swap! Clear the temp space before
    writing. Ensure a unique filename for temp space?
- [ ] Review docs for out-of-date information


### Testing

- [ ] Remove "validate" invoke task? It should instead be part of the runtime behavior,
  since much of the JSON is ingested at runtime.


### Package names

- [ ] Replace "make_" module prefix with "ingest_"? Subpackage?


### Storage structure

- [ ] Update docs to reflect storage structure
- [ ] `incoming` is mixed up with a bunch of other directories. Add a `live` directory
  which contains all the live data.
    - [ ] Update provisioning code to create this dir and set permissions
    - [ ] Manually create this dir in staging/prod
- [ ] Add an `ingest-wip` directory which contains temporary ingest WIP data
    - [ ] Update provisioning code to create this dir and set permissions
    - [ ] Manually create this dir in staging/prod


### Docker image

- [ ] Stop using `mambauser`? Volumes are always owned by `root`, and using `mambauser`
  in the container makes volume management more complex.


### Provisioning

- [ ] Ensure `${STORAGE}/regions` exists (unless a change to Docker image OBEs this
  requirement).


## 2022

### Data structure

* Split `variables.json` to `variables/raster.json` and `variables/swe.json`?


### Code organization

* How should the daily data ingest functionality and the static data be related?
  * Currently they live in the same repo and their version numbers are in lockstep.
    Consequences include: Building ingest image when only changing dynamic data and
    vice versa. Benefits include: No need to think about compatibility between static
    data versions and ingest versions.


### Data validation

* Schemas
* Validate relationships between json files


### Python tooling

* Static analysis (lint/typecheck) in CI
* A unified CLI interface for operational tooling?


### Deployment / release tooling

* Build static content into a versioned Dockerfile?
