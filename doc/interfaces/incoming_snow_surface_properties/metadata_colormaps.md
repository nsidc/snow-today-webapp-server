---
title: "Metadata: colormaps"
filters:
  - "include-code-files"
# A custom field for listing display:
provider: "Version control"
---

**Color gradients** used for visualizing a data variable.

* Colormaps definition file **MUST** be named `colormaps.json`.
* Colormaps definition file **MUST** be in compliance with the schema.
* Colormaps definition file **MUST** be ingested by copying `static/colormaps.json` from
  this repository, as this source-controlled file is the source of truth.

<details>
<summary>Schema</summary>
```{.json include="../schema/colormapsIndex.json"}
```
</details>

<details>
<summary>File contents</summary>
```{.json filename="colormaps.json" include="../static/colormaps.json"}
```
</details>
