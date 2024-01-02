---
title: "Variables: SWE point data"
filters:
  - "include-code-files"
---

Variables which are available for display as **point data** on the **map** user
interface component.

These variables **MUST** be defined in the same manner as gridded data variables. They
are identified by `"layerType": "point_swe"`.

:::{.callout-note}
This mixing of concerns causes many conditional fields and should be resolved in a
future version of the spec.

Perhaps SWE variables will have their own JSON config file.
:::
