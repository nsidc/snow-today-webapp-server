---
title: "Data: plots"
filters:
  - "include-code-files"
# A custom field for listing display:
provider: "Supercomputer"
---

**Plot data** (JSON) that are displayed on the **map** user interface component.

* Plot data files **MUST** be named according to their region and variable ID
  following the pattern `{regionId}_{variableId}.json`.
* Plot data files **MUST** be in compliance with the schema.
* Plot data files **MUST** be pushed to the `plots/` subdirectory of the incoming
  directory, e.g. `{incomingDir}/plots/11726_40.json`.



<details>
<summary>Schema</summary>
```{.json include="schema/plotData.json"}
```
</details>

<details>
<summary>Example</summary>
```{.json filename="plots/11726_40.json (example)" include="example_data/plots/11726_40.json"}
```
</details>
