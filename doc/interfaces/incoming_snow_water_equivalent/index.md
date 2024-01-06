---
title: "Incoming data: Snow water equivalent"
date: "2024-01-05"
author:
  - name: "Matt Fisher"
    orcid: "0000-0003-3260-5445"
citation: true
order: 0
filters:
  - "include-code-files"
---

**Point data** (CSV) representing Snow Water Equivalent measurement locations and their
values, to be displayed on the **map** user interface component.

This data is produced by [STswe](https://github.com/truewind/STswe), operated
externally, and pushed to NSIDC in accordance with this interface.


## Revisions

**Current version: 1.0.0beta1**

{{< include .CHANGELOG.md >}}

:::{.callout-note}
This specification will likely change soon.

We need to accept SWE data from multiple super regions, and the data needs to be sent to
us with a recognizable region ID.

It's expected that this spec will be updated with:

* New filename spec
* List of expected-supported super-regions
* Requirement for data provider to stay in sync with changes to Snow Surface Properties.
:::


## Specification

* SWE data is currently provided in a non-compliant CSV format, following the example
  below. It consists of two parts.
    * Data **MUST** include a YAML-parseable front-matter including a key
      `"SnowToday_USwest_20230920_SWEsummary.txt"`, whose value is a `YYYY-MM-DD` string
      representing the date the CSV data represents.
    * Data **MUST** include a CSV-parseable body, immediately following the front-matter
      with no separator, and continuing until the end of the file.
* SWE data files **MUST** be named `SnowToday_USwest_{YYYYMMDD}_SWEsummary.txt`, e.g.
  `SnowToday_USwest_20230920_SWEsummary.txt`.
* SWE data files **MUST** be pushed, one at a time, to the incoming dir, e.g.
  `{incomingDir}/SnowToday_USwest_20230920_SWEsummary.txt`.
* SWE CSV data **MUST** include `Name`, `Lat`, `Lon`, `Elev_m`, `SWE`, `normSWE`,
  `dSWE` columns.
    * SWE CSV data **MAY** include additional columns, but the ingest process will drop
      them.

<details>
<summary>Example</summary>
```{.yaml filename="SnowToday_USwest_20230920_SWEsummary.txt (example)" include="example_data/SnowToday_USwest_20230920_SWEsummary.txt"}
```
</details>


### Cadence

The **schedule and manner** in which **data** and **metadata** are passed from the
provider to NSIDC.

- A complete set of data files, as defined by this spec, **MUST** be pushed to the
  incoming directory each processing cycle (not necessarily daily). Data from the
  previous cycle will not be retained. Incomplete data will not be accepted.
