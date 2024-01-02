---
title: "Colormaps"
filters:
  - "include-code-files"
---

Color gradients used for visualizing a data variable.

* Colormaps definition file **MUST** be named `colormaps.json` in compliance with the schema.
* Colormaps definition file **MUST** be pushed to the root of the incoming directory,
  e.g. `{incomingDir}/colormaps.json`.

<details>
<summary>Schema</summary>
```{.json include="schema/colormapsIndex.json"}
```
</details>

<details>
<summary>Example</summary>
```{.json filename="colormaps.json (example)" include="example_data/colormaps.json"}
```
</details>
