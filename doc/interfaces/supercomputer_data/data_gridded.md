---
title: "Data: gridded" 
# A custom field for listing display:
provider: "Supercomputer"
---

**Gridded data** (Cloud Optimized GeoTIFFs) that are displayed on the **map** user
interface component.

* Gridded data files **MUST** be GeoTIFFs named according to their Super Region and
  variable ID following the pattern `{superRegionId}_{variableId}.tif`.
* Gridded data files **MUST** be provided in the projection advertised in the Super
  Region definition.
* Gridded data files **MUST** be pushed to `{incomingDir}/...` (_TODO_)
