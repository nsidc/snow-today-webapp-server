---
title: "Region Hierarchy JSON Specification"
date: "2023-10-09"
author: "Sebastien Lenard"
filters:
  - "include-code-files"
---

This is our first draft.

## Requirements

We're trying to balance all of these concerns:

- Webapp load times
- Webapp usability
- Flexibility to change front-end behavior by pushing different data from the
  supercomputer.
- Predictability in how the front-end will handle data changes (why we need a spec!)


## Specification

### Super regions

Super regions are listed in their own JSON file. These are the highest-level regions,
e.g. `US West`, `Alaska`, etc.

The webapp needs to be able to quickly load the list of super-regions so it can display
the super-region dropdown. Depending on which is selected, different sub-regions may
display.

This file will contain information about each super region:

- id
- short name
- long name

... TODO ...


### Sub regions

Any region that's not a super-region. There is one JSON file for each super region's sub
regions. E.g. `WesternUS/regions.json`.

This file will contain information about each region:

- id
- short name
- long name


... TODO ...


#### Sub region hierarchy

Sub regions fall in to a hierarchy, for example one HUC2 has many HUC4s.

... TODO ...

- How will we define metadata about collections of subregions? E.g. longname / shortname
  for collections (`HUC 2`/`Hydrologic Unit Code 2 (2 digits)`). In this case, there
  will be _many_ HUC4 collections each within a separate HUC2 collection, and we don't
  want to repeat that information.


## Examples

<details>
<summary>`region_hierarchy.json`</summary>
I believe this example doesn't quite fit with the specification outline above yet, it's
just an early draft.

```{.json include="regions.json"}
```
</details>
