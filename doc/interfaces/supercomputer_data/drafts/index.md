---
title: "Drafts"
listing:
  contents: "."
  sort: "date desc"
  type: default
  categories: true
  sort-ui: true
  filter-ui: true
page-layout: full
---
*Variables.*

I created the variables.json file and updated github:
https://github.com/nsidc/snow-today-webapp-server/blob/region-data-draft-spec-1/doc/interfaces/supercomputer_data/drafts/20231026_variables/variables.json

new attributes:
sensor, platform, algorithm, sensor_text (text to display)
color_map_id: refers to colormaps.json file

attributes removed:
enabled. Now determined by the variables attribute in root region .json
cog_path. geotiff filepath In root region .json
color_map
color_map_value_range: should be in root region .json. Still needs clarification of specs by Karl.

I also included the swe variables, which were in the original variables.json
