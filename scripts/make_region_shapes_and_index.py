"""Convert region shapefiles into GeoJSON optimized for webapp.

Shapefiles are created by Karl and Mary Jo's process on the supercomputer. There is a
shapefile for all states, one for all HUC2s, one for all HUC4s, etc.

Since the webapp needs only one shape at a time, we must split them up into separate
files, one file per region. We also must save them into a format that our web
application can understand (GeoJSON).

TODO: Do we need to simplify the shapes to optimize for storage space or data transfer?
TODO: Should we split the different categories of regions into different files?
TODO: How to organize region relationships? E.g. USwest contains all HUCs and states.
      Some HUCs contain other HUCs.
"""
import functools
import json
from pathlib import Path
from typing import Callable, Iterator

import geopandas as gpd

from constants.paths import (
    REGION_INDEX_FP,
    REPO_DATA_DIR,
    REPO_SHAPES_DIR,
    STORAGE_DIR,
)
from constants.states import STATE_ABBREVS, STATES_ENABLED
from types_.regions import (
    RegionIndex,
    RegionProcessingParams,
    RegionProcessingStruct,
    ShapefileCategory,
    SubRegion,
    SubRegionCollection,
    SubRegionCollectionProcessingParams,
    SubRegionIndex,
    SuperRegion,
)
from util.region import make_region_code
from util.simplify_geometry import simplify_geometry


# TODO: Where will we get these operationally?
SHAPEFILE_INPUT_DIR = STORAGE_DIR / 'snow_today_2.0_testing' / 'shapefiles'
USWEST_SHAPEFILES: dict[ShapefileCategory, Path] = {
    'HUC2': SHAPEFILE_INPUT_DIR / 'HUC2_9to17' / 'HUC2_9to17.shp',
    'HUC4': SHAPEFILE_INPUT_DIR / 'HUC4_9to17' / 'HUC4_9to17_in5tiles.shp',
    'State': (
        SHAPEFILE_INPUT_DIR
        / 'WesternUS_states_touching5tiles'
        / 'WesternUS_states_touching5tiles.shp'
    ),
}


def _read_shapefile(shapefile_path: Path) -> gpd.GeoDataFrame:
    shapefile_gdf = gpd.read_file(shapefile_path)
    shapefile_gdf = shapefile_gdf.to_crs(epsg=3857)
    return shapefile_gdf


def _make_uswest_super_region_gdf() -> gpd.GeoDataFrame:
    all_states_gdf = _read_shapefile(USWEST_SHAPEFILES['State'])

    enabled_states_gdf = all_states_gdf[all_states_gdf['STATE'].isin(STATES_ENABLED)]

    # Dissolve boundaries between states
    enabled_states_outline = enabled_states_gdf.drop(
        ['STATE', 'STATE_FIPS'],
        axis='columns',
    ).dissolve()

    enabled_states_outline = simplify_geometry(enabled_states_outline)

    return enabled_states_outline


def _shapefile_features(shapefiles: list[Path]) -> Iterator[gpd.GeoDataFrame]:
    for shapefile_path in shapefiles:
        shapefile_gdf = _read_shapefile(shapefile_path)

        for index in shapefile_gdf.index:
            yield shapefile_gdf.iloc[[index]]


def _make_geojson(*, feature_gdf: gpd.GeoDataFrame, name: str) -> str:
    """Make a GeoJSON from a GDF containing 1 feature."""
    if len(feature_gdf) != 1:
        raise RuntimeError(f'Expected exactly 1 feature! {feature_gdf}')

    geojson_fp = REPO_SHAPES_DIR / f'{name}.geojson'

    feature_gdf = simplify_geometry(feature_gdf)
    feature_gdf.to_file(geojson_fp, driver='GeoJSON')

    geojson_relpath = str(geojson_fp.relative_to(REPO_DATA_DIR))
    return geojson_relpath


def make_uswest_super_region_geojson() -> str:
    uswest_gdf = _make_uswest_super_region_gdf()
    geojson_fp = REPO_SHAPES_DIR / 'USwest.geojson'

    uswest_gdf.to_file(geojson_fp, driver='GeoJSON')

    geojson_relpath = str(geojson_fp.relative_to(REPO_DATA_DIR))
    return geojson_relpath


def huc_feature_to_subregion(feature_gdf: gpd.GeoDataFrame) -> tuple[str, SubRegion]:
    feature = feature_gdf.iloc[0]

    huc_cols = [col for col in feature.index if col.startswith('huc')]
    assert len(huc_cols) == 1
    huc_col_name = huc_cols[0]
    huc_id = feature[huc_col_name]
    region_code = make_region_code('USwest', 'HUC', huc_id)

    subregion: SubRegion = {
        'longname': f'HUC {huc_id}: {feature["name"]}',
        'shortname': f'HUC {huc_id}',
        'shape_path': _make_geojson(feature_gdf=feature_gdf, name=region_code),
        'enabled': not huc_id.startswith('12'),
    }
    if subregion['enabled']:
        del subregion['enabled']
    return (huc_id, subregion)


def state_feature_to_subregion(feature_gdf: gpd.GeoDataFrame) -> tuple[str, SubRegion]:
    feature = feature_gdf.iloc[0]

    state_longname = feature['STATE']
    state_abbrev = STATE_ABBREVS[state_longname]
    region_code = make_region_code('USwest', 'State', state_abbrev)

    return (
        state_abbrev,
        {
            'longname': state_longname,
            'shortname': state_abbrev,
            'shape_path': _make_geojson(feature_gdf=feature_gdf, name=region_code),
            'enabled': state_longname in STATES_ENABLED,
        },
    )


def make_subregions_from_shapefiles(
    *,
    shapefiles: list[Path],
    feature_to_subregion_fn: Callable[[gpd.GeoDataFrame], tuple[str, SubRegion]]
) -> SubRegionIndex:
    subregion_ids_and_params = sorted(
        [
            feature_to_subregion_fn(feature)
            for feature in _shapefile_features(shapefiles)
        ],
        key=lambda x: x[0],
    )
    return {
        subregion_id: subregion_params
        for subregion_id, subregion_params in subregion_ids_and_params
    }


TO_PROCESS_REGIONS: RegionProcessingStruct = {
    'USwest': {
        'longname': 'Western United States',
        'shortname': 'Western U.S.',
        'super_region_geojson_fn': make_uswest_super_region_geojson,
        'subregion_collections': {
            'HUC': {
                'longname': 'Hydrologic Unit Codes',
                'shortname': 'HUC',
                'subregion_items_fn': functools.partial(
                    make_subregions_from_shapefiles,
                    shapefiles=[
                        USWEST_SHAPEFILES['HUC2'],
                        USWEST_SHAPEFILES['HUC4'],
                    ],
                    feature_to_subregion_fn=huc_feature_to_subregion,
                ),
            },
            'State': {
                'longname': 'U.S. States',
                'shortname': 'State',
                'subregion_items_fn': functools.partial(
                    make_subregions_from_shapefiles,
                    shapefiles=[USWEST_SHAPEFILES['State']],
                    feature_to_subregion_fn=state_feature_to_subregion,
                ),
            },
        },
    },
    # TODO: 'HMA': {},
}


def _sub_region_collection_from_params(
    params: SubRegionCollectionProcessingParams,
) -> SubRegionCollection:
    return {
        'longname': params['longname'],
        'shortname': params['shortname'],
        'items': params['subregion_items_fn'](),
    }


def _super_region_from_params(params: RegionProcessingParams) -> SuperRegion:
    subregion_collections = {
        collection_id: _sub_region_collection_from_params(collection_params)
        for collection_id, collection_params in params['subregion_collections'].items()
    }
    return {
        'longname': params['longname'],
        'shortname': params['shortname'],
        'shape_path': params['super_region_geojson_fn'](),
        'subregion_collections': subregion_collections,
    }


def make_all_regions_geojson() -> RegionIndex:
    """Create a GeoJSON file for each region and sub-region.

    Return an index of regions.
    """
    return {
        region_id: _super_region_from_params(params)
        for region_id, params in TO_PROCESS_REGIONS.items()
    }


def make_region_shapes_and_index() -> None:
    region_index = make_all_regions_geojson()

    with open(REGION_INDEX_FP, 'w') as outfile:
        json.dump(region_index, outfile, sort_keys=False, indent=2)


if __name__ == '__main__':
    make_region_shapes_and_index()
