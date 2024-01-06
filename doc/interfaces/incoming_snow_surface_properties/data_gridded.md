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
* Gridded data files for different regions **MAY** be identical
  [as a consequence of the way super regions are defined on the supercomputer](https://github.com/nsidc/snow-today-webapp-server/pull/46#discussion_r1440797295).
