---
title: "Interface specifications"
listing:
  type: "table"
  sort-ui: false
  filter-ui: false
  contents:
    - "*/index.md"
---

## Terms

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


### User interface components

* **Map**: A raster visualization of a region (i.e. a land subdivision), including:
    * **Shape** of the region
    * A **gridded data variable**
    * A **NoData mask** (optional)
    * **Snow Water Equivalent point data** (optional)

* **Plot**: A line chart visualization of data about a region, including:
    * This water-year's measurements of a **plot data variable**
    * Statistical measurements calculated from full climatology for the region (i.e. the
      historical data of the same sensor/platform/variable, calculated by the
      supercomputer):
        * **Minimum**
        * **Maximum**
        * **Median**
        * **Interquartile range** (the range between 25th percentile and 75th
          percentile)


### Misc.

* **Incoming directory**: Where the supercomputer pushes files. Notated as
  `{incomingDir}` in the spec, this directory is usually
  `incoming/snow-surface-properties`, with the exception of SWE point data which goes to
  `incoming/snow-water-equivalent` directory instead.

  :::{.callout-note}
  On NSIDC infrastructure there are separate incoming directories available for testing
  (i.e. `integration`, `qa`, `staging`) and `production`.
  :::

* **Live directory**: Where the ingest application writes files for the webapp to
  access. Notated as `{liveDir}` in the spec, this directory is usually
  `live/snow-surface-properties`, with the exception of SWE point data which goes to
  `live/snow-water-equivalent` directory instead.

* **Water year**: An annual period that corresponds with regional precipitation patterns
  rather than the start and end of the calendar year. Each Super Region's water year can
  be different (e.g. the Western US water year starts on October 1), and this info is
  passed by the supercomputer as metadata.


## Specifications
