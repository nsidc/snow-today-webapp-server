# TODO

## 2024

- [ ] Review docs for out-of-date information


### Ingest

- [ ] Do validation implicitly at the right times for each ingest task. The schemas
      should validate input files as well as output files, so we can run the validation
      both before input **and** after output?


### VM provisioning

- [ ] Ensure provisioning code is creating the `live` and `ingest-wip` directories.
    - [ ] Manually create them in all prod/pre-prod envs
    - [ ] Cleanup OBE storage dirs in all envs


### Testing

- [x] Remove "validate" invoke task? It should instead be part of the runtime behavior,
      since much of the JSON is ingested at runtime.
    - [ ] Make a unit test that validates data files that are stored in the repo.
    - [x] For JSON that isn't ingested at run-time, use pre-commit to validate.


### Supercomputer interface specification

- [x] Clarify which data is sent by supercomputer and which is a static part of this
      repository. e.g. supercomputer SHOULD NOT send colormap and variable definition
      data. **Use a new field in the Quarto doc and expose it in the listing**


#### Misc. notes

* Sebastien: I created the `variables.json` file and
  [updated github](https://github.com/nsidc/snow-today-webapp-server/blob/region-data-draft-spec-1/doc/interfaces/supercomputer_data/drafts/20231026_variables/variables.json)
    - [ ] This 404s. Are we missing anything that was in this revision?


### Schemas, validation, and Python types

They really represent a lot of overlapping information.

- [ ] Use Pydantic types to generate JSON schemas:
      <https://docs.pydantic.dev/latest/concepts/json_schema/>
- [ ] Validate relationships between json files


### Old TODOs

- [ ] Is anything from 2022/2023 left incomplete?


## 2023

- [x] Write to a temporary output location and swap! Clear the temp space before
      writing. Ensure a unique filename for temp space?


### Package names

- [x] Replace "make_" module prefix with "ingest_"? Subpackage?


### Storage structure

- [ ] Update docs to reflect storage structure
- [x] `incoming` is mixed up with a bunch of other directories. Add a `live` directory
      which contains all the live data.
- [x] Add an `ingest-wip` directory which contains temporary ingest WIP data


### Docker image

- [ ] Stop using `mambauser`? Volumes are always owned by `root`, and using `mambauser`
    in the container makes volume management more complex.


## 2022

### Data structure

* Split `variables.json` to `variables/raster.json` and `variables/swe.json`?


### Code organization

* How should the daily data ingest functionality and the static data be related?
  * Currently they live in the same repo and their version numbers are in lockstep.
    Consequences include: Building ingest image when only changing dynamic data and
    vice versa. Benefits include: No need to think about compatibility between static
    data versions and ingest versions.


### Deployment / release tooling

* Build static content into a versioned Dockerfile?
