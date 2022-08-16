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
    longname: str
    shortname: str
    filename: str


class RegionIndexEntry(TypedDict):
    longname: str
    shortname: str
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

# The coefficient used to calculate the simplification threshold (by multiplying this
# number by the size of the shortest dimension of each shape's bbox). Smaller numbers
# result in finer output resolution.
# At .001, our biggest regions are 125KB. 7.2MB in total.
# At .0005, our biggest regions are 237KB. 13MB in total.
# At .0001, our biggest regions are 762KB. 41MB in total.
SIMPLIFICATION_COEFFICIENT = .0005

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


def _simplify_geometry(feature_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Simplify geometry by `SIMPLIFICATION_COEFFICIENT`.

    Calculates the simplification threshold by dividing the shortest dimension of the
    feature by `SIMPLIFICATION_COEFFICIENT`.

    E.g. if a shape's bounds are 4km x 10km, and the coefficient is 1000, the threshold
    will be 4m.
    """
    if len(feature_gdf) != 1:
        raise RuntimeError(f'Expected exactly 1 feature! {feature_gdf}')

    bounds = feature_gdf.bounds.iloc[0]

    shortest_dim = min(
        abs(bounds.maxy - bounds.miny),
        abs(bounds.maxx - bounds.minx),
    )

    threshold = shortest_dim * SIMPLIFICATION_COEFFICIENT

    feature_gdf = feature_gdf.set_geometry(
        feature_gdf['geometry'].simplify(threshold).buffer(0),
    )

    return feature_gdf


def _region_info(category: ShapefileCategory, feature: gpd.GeoSeries) -> RegionInfo:
    """Extract re-usable information from each feature."""
    if category.startswith('HUC'):
        region_type = 'HUC'

        huc_col_name = [f for f in feature.index if f.startswith('huc')][0]
        huc_id = feature[huc_col_name]

        region_longname = f'HUC {huc_id}: {feature["name"]}'
        region_shortname = f'HUC_{huc_id}'
        region_id = f'USwest_HUC_{huc_id}'
    elif category == 'State':
        region_type = 'State'
        region_longname = feature['STATE']
        region_shortname = STATE_ABBREVS[region_longname]
        region_id = f'USwest_State_{region_shortname}'
    else:
        raise RuntimeError(f'Unexpected category: {category}')

    return {
        'id': region_id,
        'type': region_type,
        'longname': region_longname,
        'shortname': region_shortname,
        'filename': f'{region_id}.geojson',
    }


def _make_geojson(category: ShapefileCategory, feature_gdf: gpd.GeoDataFrame) -> str:
    """Make a GeoJSON from a GDF containing 1 feature."""
    if len(feature_gdf) != 1:
        raise RuntimeError(f'Expected exactly 1 feature! {feature_gdf}')
    feature = feature_gdf.iloc[0]

    region_info = _region_info(category=category, feature=feature)
    geojson_fp = SHAPE_OUTPUT_DIR / region_info['filename']

    feature_gdf = _simplify_geometry(feature_gdf)
    feature_gdf.to_file(geojson_fp, driver='GeoJSON')

    return region_info


def _update_geojson_index(region_info: RegionInfo, region_index: RegionIndex):
    """Mutate `region_index` to add region defined by `region_info`."""
    if region_info['id'] in region_index.keys():
        raise RuntimeError(f'Duplicate region ID: {region_info["id"]}')

    region_index[region_info['id']] = {
        'longname': region_info['longname'],
        'shortname': region_info['shortname'],
        'file': f'shapes/{region_info["filename"]}',
        'type': region_info['type'],
    }


def make_all_geojson():
    """Create a GeoJSON file for each region (feature) in SHAPEFILES."""
    print('Creating a GeoJSON file for each feature in shapefiles:')
    print(list(SHAPEFILES.values()))

    region_index = {}

    for shapefile_category, shapefile_path in SHAPEFILES.items():
        shapefile_gdf = gpd.read_file(shapefile_path)
        shapefile_gdf = shapefile_gdf.to_crs(epsg=3857)
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
