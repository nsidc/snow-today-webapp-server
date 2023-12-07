# TODO: This whole thing is really outdated; the code doesn't need to know about HUCs at
# all.
from collections.abc import Callable
from typing import Literal

# TODO: After upgrading to 3.11 (PEP655), can use builtin TypedDict again.
#       https://peps.python.org/pep-0655/#usage-in-python-3-11
from typing_extensions import NotRequired, TypedDict

###############################################################################
# Types for region input things (e.g. magic strings in shapefiles)
###############################################################################

# The shapes for the regions come in shapefiles categorized thusly:
ShapefileCategory = Literal['HUC2', 'HUC4', 'State']


###############################################################################
# Types for region output things (e.g. magic strings, the JSON region index)
###############################################################################

# The final categorization of shapes will be:
SubRegionCollectionName = Literal['HUC', 'State']

# SuperRegionName = Literal['USwest', 'HMA']
SuperRegionName = Literal['USwest']


class SubRegion(TypedDict):
    """A member of a sub-region collection."""

    longname: str
    shortname: str
    shape_path: str
    enabled: NotRequired[bool]


SubRegionIndex = dict[str, SubRegion]


class SubRegionCollection(TypedDict):
    """A collection of sub-regions (`items`) of a particular type.

    e.g.:
        * States
        * Hydrologic Unit Codes
        * Countries
    """

    longname: str
    shortname: str
    items: SubRegionIndex


SubRegionCollectionIndex = dict[SubRegionCollectionName, SubRegionCollection]


class SuperRegion(TypedDict):
    """A large primary region containing many collections of sub-regions."""

    longname: str
    shortname: str
    shape_path: str
    subregion_collections: SubRegionCollectionIndex


RegionIndex = dict[str, SuperRegion]


###############################################################################
# Types used in processing input -> output
###############################################################################


class SubRegionCollectionProcessingParams(TypedDict):
    longname: str
    shortname: str
    subregion_items_fn: Callable[[], SubRegionIndex]


class RegionProcessingParams(TypedDict):
    longname: str
    shortname: str
    super_region_geojson_fn: Callable[[], str]  # Returns the "shape_path" string
    subregion_collections: dict[
        SubRegionCollectionName,
        SubRegionCollectionProcessingParams,
    ]


RegionProcessingStruct = dict[SuperRegionName, RegionProcessingParams]
