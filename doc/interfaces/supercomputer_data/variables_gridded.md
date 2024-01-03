---
title: "Variables: gridded data"
filters:
  - "include-code-files"
---

Variables which are available for display as **gridded data** on the **map** user interface
component.

* Variables definition file **MUST** be named `variables.json`.
* Variables definition file **MUST** be in compliance with the schema.
* Variables definition file **MUST** be ingested by copying `static/variables.json` from
  this repository, as this source-controlled file is the source of truth.

The NoData Mask is identified by `"layerType": "raster_notprocessed"`.

:::{.callout-note}
This mixing of concerns causes many conditional fields and should be resolved in a
future version of the spec.

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
