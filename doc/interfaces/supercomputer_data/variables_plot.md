---
title: "Variables: plot data"
filters:
  - "include-code-files"
---

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
