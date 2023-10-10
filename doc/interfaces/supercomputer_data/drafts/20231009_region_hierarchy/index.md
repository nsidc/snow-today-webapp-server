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
<summary>`root_regions.json`</summary>
```{.json include="root_regions.json"}
```
</details>

<details>
<summary>`region_26000.json`</summary>
```{.json include="region_26000.json"}
```
</details>

<details>
<summary>`region_26101.json`</summary>
```{.json include="region_26101.json"}
```
</details>

<details>
<summary>`region_hierarchy_26000.json`</summary>
```{.json include="region_hierarchy_26000.json"}
```
</details>

<details>
<summary>`region_hierarchy_26101.json`</summary>
```{.json include="region_hierarchy_26101.json"}
```
</details>


## Notes

I feel that we'll need a dedicated specification for the categorization of regions. E.g.

`region_category_26000.json`
```json
{
  "HUC2": {"long-name": "Hydrologic Unit Code (2-digit)"},
  "USSTATE": {"long-name": "U.S. State"}
}
```

and the hierarchy can define regions as members of categories instead of assigning
regions to categories as an attribute of a region. e.g.:

`region_hierarchy_26000.json`
```json
{
  "HUC2": {
    "children": {
      "123123": {
        "name": "HUC10",
        "children": {
          "HUC4": {
            "234234": {
              "name": "HUC1010",
              "children": {
                "HUC6": {
                  "345345": {
                    "name": "HUC101010"
                  },
                  "345346": {
                    "name": "HUC101011"
                  },
                  "345347": {
                    "name": "HUC101012"
                  }
                }
              }
            },
            "234234": {
              "name": "HUC1011",
              "children": {
                "HUC6": {
                  "445345": {
                    "name": "HUC101110"
                  },
                  "445346": {
                    "name": "HUC101111"
                  },
                  "445347": {
                    "name": "HUC101112"
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Here, top-level keys and keys that are members of `children` dicts are collection
identifiers, e.g. `HUC2` corresponds to `Hydrologic Unit Code (2-digit)` from
`region_category_26000.json`.

Perhaps instead of `children`, `items` is a more conventional name for members of a
collection?
