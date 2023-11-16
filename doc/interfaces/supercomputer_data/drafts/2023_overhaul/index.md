---
title: "Supercomputer interface specification overhaul"
date: "2023-11-16"
author:
  - name: "Sebastien Lenard"
    orcid: "0000-0003-3358-7197"
  - name: "Matt Fisher"
    orcid: "0000-0003-3260-5445"
citation: true
filters:
  - "include-code-files"
---

Our goal is to overhaul the interface between the supercomputer and the webapp to
provide a more data-driven interface, for example to allow new regions, variables,
sensors, colormaps, etc. to be added without a code change.

We need to to balance all of these concerns:

- Webapp load time: startup load time, and load time when changing regions & variables
- Webapp maintainability
- Flexibility to change webapp behavior by pushing different data from the
  supercomputer.
- Predictability in how the webapp will respond to data changes


## Terms

### RFC2119

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and **OPTIONAL**
are defined by [RFC2119](https://www.ietf.org/rfc/rfc2119.txt).


### Components

* **webapp**: Because the webapp has a client and server component, avoid the confusing
  term "front-end".
* **webapp server** or **webapp back-end**: The thing that provides web-friendly data to
  the front-end.
* **webapp ingest**: The thing that turns supercomputer data into web-friendly data for
  the webapp server. **This component _receives_ data over the interface specified by this
  document.**
* **supercomputer** or **supercomputer back-end**: Where the original data is produced.
  **This component _sends_ data over the interface specified by this document.**


## Principles

- The webapp should be able to selectively load Sub Region data by selected Super Region
    - _Rationale: minimizes webapp start-up time and overall download._
- Everything has an ID
    - _Rationale: enables building relationships between Regions, Variables, etc.
      without sending too much extraneous data._
- Relative paths are relative to API root
    - _Rationale: it's less stateful to reconstruct a URL this way (as opposed to if the
      relative path was relative to the file containing it)_
- Data from the supercomputer *MAY* be unminified.
    - _Rationale: it can be minified on ingest._
- JSON attributes are `camelCase`.
    - _Rationale: consistency is good, it doesn't matter what we pick._


## Regions

{{< include regions.md >}}


## Variables

{{< include variables.md >}}
