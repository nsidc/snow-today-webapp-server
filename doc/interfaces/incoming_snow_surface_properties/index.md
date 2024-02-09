---
title: "Incoming data: Snow surface properties"
date: "2024-01-05"
author:
  - name: "Sebastien Lenard"
    orcid: "0000-0003-3358-7197"
  - name: "Matt Fisher"
    orcid: "0000-0003-3260-5445"
citation: true
order: 0
listing:
  type: "table"
  sort-ui: false
  filter-ui: false
  contents:
    - "."
  fields:
    - "title"
    - "description"
    - "provider"
  field-display-names:
    provider: "Provider"
---

The supercomputer processes data with [esp](https://github.com/sebastien-lenard/esp) and
sends it, with SCP, to an NSIDC disk, in accordance with this interface. From here, the
webapp back-end picks it up to prepare it for visualization by the webapp.

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

:::{.callout-important}
All **data** and **metadata** has a provider.

* **Version control**: Data is version-controlled in this repository's `static/`
  directory.
* **Supercomputer**: Data is pushed dynamically on a schedule from the supercomputer.
:::
