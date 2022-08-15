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
import json
from pathlib import Path
from typing import Literal, TypedDict

import geopandas as gpd


# Types
ShapefileCategory = Literal['HUC2', 'HUC4', 'State']
RegionType = Literal['HUC', 'State']


class RegionInfo(TypedDict):
    id: str
    type: RegionType
    name: str
    code: str
    fn: str


class RegionIndexEntry(TypedDict):
    longname: str
    file: str
    type: RegionType


RegionIndex = dict[str, RegionIndexEntry]

# Constants
REPO_DIR = Path(__file__).parent.parent.absolute()
REPO_DATA_DIR = REPO_DIR / 'data'
SHAPE_OUTPUT_DIR = REPO_DATA_DIR / 'shapes'
REGION_INDEX_FP = REPO_DATA_DIR / 'regions.json'

SHAPEFILE_INPUT_DIR = Path('/share/apps/snow-today/snow_today_2.0_testing/shapefiles')
SHAPEFILES: dict[ShapefileCategory, Path] = {
    'HUC2': SHAPEFILE_INPUT_DIR / 'HUC2_9to17' / 'HUC2_9to17.shp',
    'HUC4': SHAPEFILE_INPUT_DIR / 'HUC4_9to17' / 'HUC4_9to17_in5tiles.shp',
    'State': SHAPEFILE_INPUT_DIR / 'WesternUS_states_touching5tiles' / 'WesternUS_states_touching5tiles.shp',
}
# NOTE: It would be really nice if the state abbreviation was included on the feature
# data, but it's not!
STATES_BY_ABBREV = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}
STATE_ABBREVS = {v: k for k, v in STATES_BY_ABBREV.items()}


def _region_code(region_type: RegionType, region_id: str) -> str:
    """Unique identifier for a region."""
    return f'USwest_{region_type}_{region_id}'


def _region_info(category: ShapefileCategory, feature: gpd.GeoSeries) -> RegionInfo:
    """Extract re-usable information from each feature."""
    if category.startswith('HUC'):
        region_type = 'HUC'
        huc_col_name = [f for f in feature.index if f.startswith('huc')][0]
        region_id = feature[huc_col_name]
        region_name = f'HUC{feature["name"]}'
    elif category == 'State':
        region_type = 'State'
        region_name = feature['STATE']
        region_id = STATE_ABBREVS[region_name]
    else:
        raise RuntimeError(f'Unexpected category: {category}')

    region_code = _region_code(region_type, region_id)
    return {
        'id': region_id,
        'type': region_type,
        'name': region_name,
        'code': region_code,
        'fn': f'{region_code}.geojson',
    }


def _make_geojson(category: ShapefileCategory, feature_gdf: gpd.GeoDataFrame) -> str:
    """Make a GeoJSON from a GDF containing 1 feature."""
    if len(feature_gdf) != 1:
        raise RuntimeError(f'Expected exactly 1 feature! {feature_gdf}')
    feature = feature_gdf.iloc[0]

    region_info = _region_info(category=category, feature=feature)
    geojson_fp = SHAPE_OUTPUT_DIR / region_info['fn']

    feature_gdf.to_file(geojson_fp, driver='GeoJSON')

    return region_info


def _update_geojson_index(region_info: RegionInfo, region_index: RegionIndex):
    """Mutate `region_index` to add region defiend by `region_info`."""
    if region_info['id'] in region_index.keys():
        raise RuntimeError(f'Duplicate region ID: {region_info["id"]}')

    region_index[region_info['code']] = {
        'longname': region_info['name'],
        'shortname': region_info['id'],
        'file': f'shapes/{region_info["fn"]}',
        'type': region_info['type'],
    }


def make_all_geojson():
    """Create a GeoJSON file for each region (feature) in SHAPEFILES."""
    print('Creating a GeoJSON file for each feature in shapefiles:')
    print(list(SHAPEFILES.values()))

    region_index = {}

    for shapefile_category, shapefile_path in SHAPEFILES.items():
        shapefile_gdf = gpd.read_file(shapefile_path)
        for index in shapefile_gdf.index:
            feature_gdf = shapefile_gdf.iloc[[index]]

            region_info = _make_geojson(
                category=shapefile_category,
                feature_gdf=feature_gdf,
            )
            _update_geojson_index(
                region_info=region_info,
                region_index=region_index,
            )

    return region_index


if __name__ == '__main__':
    region_index = make_all_geojson()

    with open(REGION_INDEX_FP, 'w') as outfile:
        json.dump(region_index, outfile, sort_keys=True, indent=4)
