---
title: "Supercomputer data interface specification"
date: "2024-01-02"
author:
  - name: "Sebastien Lenard"
    orcid: "0000-0003-3358-7197"
  - name: "Matt Fisher"
    orcid: "0000-0003-3260-5445"
citation: true
listing:
  type: "table"
  contents:
    - "*.md"
  fields:
    - "title"
    - "description"
---

The webapp data interface represents the **input** of the `snow_today_webapp_ingest`
Python code in this repository.

The supercomputer processes data and sends it, with SCP, to an NSIDC disk. From here,
the webapp back-end picks it up to prepare it for visualization by the webapp.

Allowing the supercomputer to be responsible for producing data and metadata, the webapp
can focus on visualization and changes, for example adding new regions, won't depend on
the webapp to be also updated.

We need to to balance all of these concerns:

- Webapp load time: startup load time, and load time when changing regions & variables
- Webapp maintainability
- Flexibility to change webapp behavior by pushing different data from the
  supercomputer.
- Predictability in how the webapp will respond to data changes


## Revisions

**Current version: 1.0.0beta1**

{{< include .CHANGELOG.md >}}


## Terms

* **Incoming directory**: Notated as `{incomingDir}` in the spec, this directory is
  usually `incoming/snow-surface-properties`, with the exception of SWE point data which
  goes to `incoming/snow-water-equivalent` directory instead.
* **Water year**: An annual period that corresponds with regional melt patterns rather
  than the start and end of the calendar year. Each region's water year can be
  different.


### RFC2119

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and **OPTIONAL**
are defined by [RFC2119](https://www.ietf.org/rfc/rfc2119.txt).


### Technical components

* **webapp**: Because the webapp has a client and server component, avoid the confusing
  term "front-end".
* **webapp server** or **webapp back-end**: The thing that provides web-friendly data to
  the front-end.
* **webapp ingest**: The thing that turns supercomputer data into web-friendly data for
  the webapp server. **This component _receives_ data over the interface specified by this
  document.**
* **supercomputer** or **supercomputer back-end**: Where the original data is produced.
  **This component _sends_ data over the interface specified by this document.**

:::{.callout-note}
Only the latter two components are impacted by this specification.
:::


### User interface components

* **Map**: A raster visualization of a region, including:
    * **Shape** of the region
    * A **gridded data variable**
    * A **NoData mask** (optional)
    * **Snow Water Equivalent point data** (optional)

* **Plot**: A line chart visualization of data about a region, including:
    * This water-year's measurements of a **plot data variable**
    * Statistical measurements calculated from full climatology for the region:
        * **Minimum**
        * **Maximum**
        * **Median**
        * **Interquartile range**


## Principles

- The webapp should be able to selectively load Sub Region data by selected Super Region
    - _Rationale: minimizes webapp start-up time and overall download._
- Everything has an ID
    - _Rationale: enables building relationships between Regions, Variables, etc.
      without sending too much extraneous data._
- Relative paths are relative to API root
    - _Rationale: it's less stateful to reconstruct a URL this way (as opposed to if the
      relative path was relative to the file containing it)_
- Data from the supercomputer **MAY** be unminified.
    - _Rationale: it can be minified on ingest._
- JSON attributes are `camelCase`.
    - _Rationale: consistency is good, it doesn't matter what we pick._


## Specification
