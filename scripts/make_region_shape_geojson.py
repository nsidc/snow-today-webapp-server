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
import os
from pathlib import Path
from typing import Literal

import geopandas as gpd
# TODO: After upgrading to 3.11 (PEP655), can use builtin TypedDict again.
#       https://peps.python.org/pep-0655/#usage-in-python-3-11
from typing_extensions import NotRequired, TypedDict


# Types
ShapefileCategory = Literal['HUC2', 'HUC4', 'State']
RegionType = Literal['HUC', 'State'] | None


class UnsupportedRegion(Exception):
    pass


class RegionInfo(TypedDict):
    id: str
    type: RegionType
    longname: str
    shortname: str
    filename: str
    enabled: bool


class RegionIndexEntry(TypedDict):
    longname: str
    shortname: str
    file: str
    type: RegionType
    enabled: NotRequired[bool]


RegionIndex = dict[str, RegionIndexEntry]

# Constants
REPO_DIR = Path(__file__).parent.parent.absolute()
REPO_DATA_DIR = REPO_DIR / 'data'
SHAPE_OUTPUT_DIR = REPO_DATA_DIR / 'shapes'
REGION_INDEX_FP = REPO_DATA_DIR / 'regions.json'

try:
    STORAGE_DIR = Path(os.environ['STORAGE_DIR'])
except Exception as e:
    raise RuntimeError(
        f'Expected $STORAGE_DIR envvar to be populated: {e}'
    )

SHAPEFILE_INPUT_DIR = STORAGE_DIR / 'snow_today_2.0_testing' / 'shapefiles'
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
# NOTE: It would be really nice if the input data only included the needed regions, but
# it may contain any.
STATES_BY_ABBREV = {
    'AK': {
        'longname': 'Alaska',
        'enabled': False,
    },
    'AL': {
        'longname': 'Alabama',
        'enabled': False,
    },
    'AR': {
        'longname': 'Arkansas',
        'enabled': False,
    },
    'AZ': {
        'longname': 'Arizona',
        'enabled': True,
    },
    'CA': {
        'longname': 'California',
        'enabled': True,
    },
    'CO': {
        'longname': 'Colorado',
        'enabled': True,
    },
    'CT': {
        'longname': 'Connecticut',
        'enabled': False,
    },
    'DC': {
        'longname': 'District of Columbia',
        'enabled': False,
    },
    'DE': {
        'longname': 'Delaware',
        'enabled': False,
    },
    'FL': {
        'longname': 'Florida',
        'enabled': False,
    },
    'GA': {
        'longname': 'Georgia',
        'enabled': False,
    },
    'HI': {
        'longname': 'Hawaii',
        'enabled': False,
    },
    'IA': {
        'longname': 'Iowa',
        'enabled': False,
    },
    'ID': {
        'longname': 'Idaho',
        'enabled': True,
    },
    'IL': {
        'longname': 'Illinois',
        'enabled': False,
    },
    'IN': {
        'longname': 'Indiana',
        'enabled': False,
    },
    'KS': {
        'longname': 'Kansas',
        'enabled': False,
    },
    'KY': {
        'longname': 'Kentucky',
        'enabled': False,
    },
    'LA': {
        'longname': 'Louisiana',
        'enabled': False,
    },
    'MA': {
        'longname': 'Massachusetts',
        'enabled': False,
    },
    'MD': {
        'longname': 'Maryland',
        'enabled': False,
    },
    'ME': {
        'longname': 'Maine',
        'enabled': False,
    },
    'MI': {
        'longname': 'Michigan',
        'enabled': False,
    },
    'MN': {
        'longname': 'Minnesota',
        'enabled': False,
    },
    'MO': {
        'longname': 'Missouri',
        'enabled': False,
    },
    'MS': {
        'longname': 'Mississippi',
        'enabled': False,
    },
    'MT': {
        'longname': 'Montana',
        'enabled': True,
    },
    'NC': {
        'longname': 'North Carolina',
        'enabled': False,
    },
    'ND': {
        'longname': 'North Dakota',
        'enabled': False,
    },
    'NE': {
        'longname': 'Nebraska',
        'enabled': True,
    },
    'NM': {
        'longname': 'New Mexico',
        'enabled': True,
    },
    'NH': {
        'longname': 'New Hampshire',
        'enabled': False,
    },
    'NJ': {
        'longname': 'New Jersey',
        'enabled': False,
    },
    'NV': {
        'longname': 'Nevada',
        'enabled': True,
    },
    'NY': {
        'longname': 'New York',
        'enabled': False,
    },
    'OH': {
        'longname': 'Ohio',
        'enabled': False,
    },
    'OK': {
        'longname': 'Oklahoma',
        'enabled': False,
    },
    'OR': {
        'longname': 'Oregon',
        'enabled': True,
    },
    'PA': {
        'longname': 'Pennsylvania',
        'enabled': False,
    },
    'RI': {
        'longname': 'Rhode Island',
        'enabled': False,
    },
    'SC': {
        'longname': 'South Carolina',
        'enabled': False,
    },
    'SD': {
        'longname': 'South Dakota',
        'enabled': True,
    },
    'TN': {
        'longname': 'Tennessee',
        'enabled': False,
    },
    'TX': {
        'longname': 'Texas',
        'enabled': False,
    },
    'UT': {
        'longname': 'Utah',
        'enabled': True,
    },
    'VA': {
        'longname': 'Virginia',
        'enabled': False,
    },
    'VT': {
        'longname': 'Vermont',
        'enabled': False,
    },
    'WA': {
        'longname': 'Washington',
        'enabled': True,
    },
    'WI': {
        'longname': 'Wisconsin',
        'enabled': False,
    },
    'WY': {
        'longname': 'Wyoming',
        'enabled': True,
    },
}
STATE_ABBREVS = {v['longname']: k for k, v in STATES_BY_ABBREV.items()}
STATES_ENABLED = {v['longname'] for v in STATES_BY_ABBREV.values() if v['enabled']}


def _simplify_geometry(feature_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Simplify geometry by `SIMPLIFICATION_COEFFICIENT`.

    Calculates the simplification threshold by multiplying the shortest dimension of the
    feature by `SIMPLIFICATION_COEFFICIENT`.

    E.g. if a shape's bounds are 4km x 10km, and the coefficient is .001, the threshold
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
    region_enabled: boolean = True

    if category.startswith('HUC'):
        region_type = 'HUC'

        huc_col_name = [f for f in feature.index if f.startswith('huc')][0]
        huc_id = feature[huc_col_name]

        if huc_id.startswith('12'):
            region_enabled = False

        region_longname = f'HUC {huc_id}: {feature["name"]}'
        region_shortname = f'HUC_{huc_id}'
        region_id = f'USwest_HUC_{huc_id}'
    elif category == 'State':
        region_type = 'State'
        region_longname = feature['STATE']
        region_shortname = STATE_ABBREVS[region_longname]
        region_enabled = region_longname in STATES_ENABLED

        region_id = f'USwest_State_{region_shortname}'
    else:
        raise RuntimeError(f'Unexpected category: {category}')

    region_info = {
        'id': region_id,
        'type': region_type,
        'longname': region_longname,
        'shortname': region_shortname,
        'filename': f'{region_id}.geojson',
        'enabled': region_enabled,
    }

    return region_info


def _make_uswest_region_geojson(all_states_gdf: gpd.GeoDataFrame) -> RegionInfo:
    region_info: RegionInfo = {
        'id': 'USwest',
        'type': None,
        'longname': 'US West complete',
        'shortname': 'USwest',
        'filename': 'USwest.geojson',
        'enabled': True,
    }
    geojson_fp = SHAPE_OUTPUT_DIR / region_info['filename']

    enabled_states_gdf = all_states_gdf[all_states_gdf['STATE'].isin(STATES_ENABLED)]
    # Dissolve boundaries between states
    enabled_states_outline = enabled_states_gdf.drop(
        ['STATE', 'STATE_FIPS'],
        axis='columns',
    ).dissolve()

    enabled_states_outline = _simplify_geometry(enabled_states_outline)
    enabled_states_outline.to_file(geojson_fp, driver='GeoJSON')

    return region_info


def _make_geojson(category: ShapefileCategory, feature_gdf: gpd.GeoDataFrame) -> RegionInfo:
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
    if region_info['enabled'] is False:
        region_index[region_info['id']]['enabled'] = False


def make_all_geojson():
    """Create a GeoJSON file for each region (feature) in SHAPEFILES."""
    print('Creating a GeoJSON file for each feature in shapefiles:')
    print(list(SHAPEFILES.values()))

    region_index = {}

    for shapefile_category, shapefile_path in SHAPEFILES.items():
        shapefile_gdf = gpd.read_file(shapefile_path)
        shapefile_gdf = shapefile_gdf.to_crs(epsg=3857)

        # Make shape of full USwest region:
        if shapefile_category == 'State':
            region_info = _make_uswest_region_geojson(shapefile_gdf)
            _update_geojson_index(
                region_info=region_info,
                region_index=region_index,
            )

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

    # TODO: Re-order?

    with open(REGION_INDEX_FP, 'w') as outfile:
        json.dump(region_index, outfile, sort_keys=True, indent=4)
