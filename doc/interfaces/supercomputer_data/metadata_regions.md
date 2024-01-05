---
title: "Metadata: regions"
filters:
  - "include-code-files"
# A custom field for listing display:
provider: "Supercomputer"
---

Any **region** that can be selected for viewing on the map or plot.
Includes **Super Regions** and **Sub Regions** and information about their
relationships..

- All regions (Super Regions and Sub Regions) **MUST** have a unique numeric region
  identifier.
    - Regions and Region Collections **MUST NOT** be identified by any of the following
      reserved strings:
        - `undefined`
        - `regions`
        - `collections`
        - `metadata`


### Super Regions

These are top-level regions, e.g. "Western U.S.", "Canada".
The webapp needs to be able to quickly load the list of super-regions so it can display
a selector to the user. Depending on which is selected, different sub-regions may
display.

- Super Regions definition file **MUST** be named `root.json`.
- Super Regions definition file **MUST** be in compliance with the schema.
- Super Regions definition file **MUST** be pushed to the `regions/` subdirectory of the
  incoming directory, e.g. `{incomingDir}/regions/root.json`.
- Super Regions **MAY** be omitted from the Super Regions definition file if no variable
  are visible for the super region.

  :::{.callout-note}
  In a future version of the schema, we should offer a boolean config option `enabled`
  and recommend setting it to false to omit a region.
  :::

- Super Regions with no Sub Regions/Collections **MAY** be included in the Super Regions
  definition file.
- Relationships with variables **MUST** be defined at the Super Region level, and those
  relationships **MUST** be considered inherited by all their Sub Regions.
- The following Super Regions **MUST** always be assigned the following identifiers.
  This is to enable Snow Surface Properties and Snow Water Equivalent codebases to be
  compatible.
    - Western US: `26000`
    - Alaska: `26100`
    - Canada: `26101`

<details>
<summary>Schema</summary>
```{.json include="schema/regionsIndex.json"}
```
</details>

<details>
<summary>Example</summary>
```{.json filename="regions/root.json (example)" include="example_data/regions/root.json"}
```
</details>


### Sub Regions

Any region that is a member of a Super Region (and therefore, cannot be a Super Region
itself).

- Sub Regions definition files **MUST** be named according to the Super Region they are
  a member of in `{superRegionId}.json`, e.g. `26000.json`.
- Sub Regions definition files **MUST** be in compliance with the schema.
- Sub Regions definition files **MUST** be pushed to the `regions/` subdirectory of the
  incoming directory, e.g. `{incomingDir}/regions/26000.json`.
- Sub Regions **MUST** be a member of a Region Collection.
- Sub Regions **MAY** contain one or more Sub Region Collections.

<details>
<summary>Schema</summary>
```{.json include="schema/subRegionsIndex.json"}
```
</details>

<details>
<summary>Example</summary>
```{.json filename="regions/26000.json" include="example_data/regions/26000.json"}
```
</details>


## Sub Region Collections

A collection containing Sub Regions.

- Collection definition file **MUST** be named `collections.json`.
- Collection definition file **MUST** be in compliance with the schema.
- Collection definition file **MUST** be pushed to the `regions/` subdirectory of the
  incoming directory, e.g. `{incomingDir}/regions/collections.json`.
- A collection **MUST** contain one or many Sub Region members.

<details>
<summary>Schema</summary>
```{.json include="schema/subRegionCollectionsIndex.json"}
```
</details>

<details>
<summary>Example</summary>
```{.json filename="regions/collections.json" include="example_data/regions/collections.json"}
```
</details>


## Sub Region Hierarchy

An expression of relationships between Sub Regions. E.g.:

* A State/Province may contain many multiple State subdivisions.
* A HUC2 Sub Region may contain a HUC4 Sub Region Collection containing multiple HUC4
  Sub Regions, each containing a collection of HUC 6 Sub Regions.

The hierarchy can be arbitrarily deep.

- Sub Region Hierarchy definition files **MUST** be named according to the Super Region
  they are a member of in `{superRegionId}_hierarchy.json`, e.g.
  `26000_hierarchy.json`.
- Sub Region Hierarchy definition files **MUST** be in compliance with the schema.
- Sub Region Hierarchy definition files **MUST** be pushed to the `regions/`
  subdirectory of the incoming directory, e.g.
  `{incomingDir}/regions/26000_hierarchy.json`.

<details>
<summary>Schema</summary>
```{.json include="schema/subRegionsHierarchy.json"}
```
</details>

<details>
<summary>Example</summary>
```{.json include="example_data/regions/26000_hierarchy.json"}
```
</details>


## Region Shapes

GeoJSON files representing the shapes of regions.

- Region Shapes definition files **MUST** be named according to their unique region
  identifier, e.g.  `26000.geojson`.
- Region Shapes definition files **MUST** be , in compliance with the schema.
- Region Shapes definition files **MUST** be pushed to the `regions/shapes/`
  subdirectory of the incoming directory.
- Region Shapes definition files **MUST** be organized in to sub-directories based on
  the first two digits of their unique region identifier, e.g.
  `{incomingDir}/regions/shapes/26/26000.geojson`.
- Region Shapes **MUST** be provided for each defined Super Region and Sub Region.

<details>
<summary>Example</summary>
```{.json include="example_data/regions/shapes/26/26000.geojson"}
```
</details>
