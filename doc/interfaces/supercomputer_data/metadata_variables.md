---
title: "Metadata: variables"
filters:
  - "include-code-files"
# A custom field for listing display:
provider: "Version control"
---

Variables which are available for display either as **gridded data** on the **map** user
interface component, as a **line chart** on the **plot** UI component, or as **SWE
points** on the **map** UI component.

:::{.callout-note}
This mixing of concerns causes many conditional fields and should be resolved in a
future version of the spec. The subsections which follow elaborate on this.
:::

* Variables definition file **MUST** be named `variables.json`.
* Variables definition file **MUST** be in compliance with the schema.
* Variables definition file **MUST** be ingested by copying `static/variables.json` from
  this repository, as this source-controlled file is the source of truth.

The NoData Mask is identified by `"layerType": "raster_notprocessed"`.

:::{.callout-note}
The NoData mask, to me, doesn't make sense as a variable, and this should be resolved in
a future version of the spec.

Perhaps the NoData mask will have its own JSON config file.
:::

<details>
<summary>Schema</summary>
```{.json include="schema/variablesIndex.json"}
```
</details>

<details>
<summary>File contents</summary>
```{.json filename="variables.json" include="static/variables.json"}
```
</details>


## Gridded data variables

This is the "normal" case `variables.json` was designed for. The other types of data
were tacked on.


## Plot data variables

Variables which are available for display as **line chart** in the **plot** user
interface component.

These variables **MUST** be defined in the same manner as gridded data variables, and in
fact share an ID with gridded data variables.

:::{.callout-note}
This mixing of concerns assumes a 1:1 relationship between gridded data variables and
plot data variables.

If that assumption is valid, and both NoData and SWE variables can be extracted from the
gridded variables specification, then perhaps plot variables and gridded data variables
should continue to share an ID.
:::


## SWE point data variables

Variables which are available for display as **point data** on the **map** user
interface component.

These variables **MUST** be defined in the same manner as gridded data variables. They
are identified by `"layerType": "point_swe"`.

:::{.callout-note}
This mixing of concerns causes many conditional fields and should be resolved in a
future version of the spec.

Perhaps SWE variables will have their own JSON config file.
:::
