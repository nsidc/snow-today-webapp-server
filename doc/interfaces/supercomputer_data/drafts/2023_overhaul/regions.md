### Specification

- All region files defined here **MUST** be pushed from the supercomputer each
  processing cycle.
- Regions and Region Collections **MUST NOT** be identified by any of the following
  reserved strings:
    - `undefined`
    - `regions`
    - `collections`
    - `metadata`


#### Regions

Any region that can be selected for viewing on the map or plot.
Includes Super Regions and Sub Regions.


##### Super Regions

These are top-level regions, e.g. "Western U.S.", "Canada".
The webapp needs to be able to quickly load the list of super-regions so it can display
a selector to the user. Depending on which is selected, different sub-regions may
display.

- Super Regions **MUST** be defined in `regions/root.json`.
- Super Regions **MAY** be omitted from `regions/root.json` if no variable are visible
  for the super region.
    - TODO: Also offer a config option `enabled: boolean`? E.g. It is **RECOMMENDED** to
      instead set `"enabled": false`.
- Super Regions with no Sub Regions/Collections **MAY** be included in
  `regions/root.json`.
- Super Regions **MUST** have the following fields:
    - TODO

<details>
<summary>Example `regions/root.json`</summary>
```{.json include="example_data/regions/root.json"}
```
</details>


##### Sub Regions

Any region that is not a Super Region. Can be anywhere in the hierarchy. Must be a
member of a Region Sollection.

- Sub Regions **MUST** be defined according to the Super Region they are a member of in
  `regions/{superRegionId}.json`, e.g. `regions/26000.json`.
- Sub Regions **MAY** contain one or more Sub Region Collections.

<details>
<summary>Example `regions/26000.json`</summary>
```{.json include="example_data/regions/26000.json"}
```
</details>


#### Sub Region Collections

A collection containing Sub Regions.

- Collections **MUST** be defined in a file `regions/collections.json`.
- A collection **MUST** contain one or many Sub Region members.

<details>
<summary>Example `regions/collections.json`</summary>
```{.json include="example_data/regions/collections.json"}
```
</details>


#### Sub Region Hierarchy

An expression of relationships between Sub Regions. E.g. a HUC2 Sub Region may contain a
HUC4 Sub Region Collection containing multiple HUC4 Sub Regions, each of which may
contain a HUC 6 SubRegion Collection. The hierarchy can be arbitrarily deep.

- Relationships between regions **MUST** be defined according to the Super Region they
  are a member of in `regions/{superRegionId}_hierarchy.json`, e.g.
  `regions/26000_hierarchy.json`.

<details>
<summary>Example `regions/26000_hierarchy.json`</summary>
```{.json include="example_data/regions/26000_hierarchy.json"}
```
</details>


### TODO

- Incorporate `root_regions_proposal.json` fields in `example_data/`


#### Sebastien notes

The root regions now include available variables for each root region, grouped by
sensor, and alphabetically ordered. New attributes:

- `isDefault`. When = 1, means web-app select by default the sensor/source and variable
- `colormap_value_range`: dynamic for snow cover days. Development required for other
  variables to make it kind of dynamic (wait for Karl specs)
- `geotiffRelativePath`: path of the geotiff
- `waterYear` of data. Dev required for dynamic
- `lastDateWithData`. idem
- `historicStartWaterYear`: oldest water year with data
- `historicSource`: indicate if source of historic is JPL or DAAC or a mix.

NB: a dev is required to make the list of variables dynamic depending on the actual
available data. [Matt] Need help to understand this part!
