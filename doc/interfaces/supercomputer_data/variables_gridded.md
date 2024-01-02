---
title: "Variables: gridded data"
filters:
  - "include-code-files"
---

Variables which are available for display as **gridded data** on the **map** user interface
component.

* Variables definition file **MUST** be named `variables.json` in compliance with the schema.
* Variables definition file **MUST** be pushed to the root of the incoming directory,
  e.g. `{incomingDir}/variables.json`.

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
<summary>Example</summary>
```{.json filename="variables.json (example)" include="example_data/variables.json"}
```
</details>
