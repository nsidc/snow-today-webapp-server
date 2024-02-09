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
* Requirement for data provider to stay in sync with changes to Snow Surface Properties'
  region definitions.  The
  [source of truth](https://github.com/sebastien-lenard/esp/blob/master/tbx/conf/configuration_of_landsubdivisions.csv)
  is available in a private GitHub repo.
:::


## Specification
