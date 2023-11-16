### Colormaps

* Colormaps **MUST** be defined in `colormaps.json`.

<details>
<summary>Example `colormaps.json`</summary>
```{.json include="example_data/colormaps.json"}
```
</details>


### Variables

We're only concerned with definitions for variables; availability of variables is on a
per-region basis in `regions/root.json`.

* Variables **MUST** be defined in `variables.json`.

<details>
<summary>Example `variables.json`</summary>
```{.json include="example_data/variables.json"}
```
</details>


### Sebastien notes

I created the `variables.json` file and [updated github](https://github.com/nsidc/snow-today-webapp-server/blob/region-data-draft-spec-1/doc/interfaces/supercomputer_data/drafts/20231026_variables/variables.json)

#### new attributes

* `sensor`, `platform`, `algorithm`, `sensor_text` (text to display)
* `color_map_id`: refers to colormaps.json file

#### attributes removed

* `enabled`: Now determined by the variables attribute in `regions/root.json`, because
  different variables can be enabled for different regions.
* `cog_path`: geotiff filepath In `regions/root.json`
* `color_map`
* `color_map_value_range`: should be in `regions/root.json`. Still needs clarification
  of specs by Karl.

I also included the SWE variables, which were in the original `variables.json`
