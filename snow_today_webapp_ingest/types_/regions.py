import datetime as dt
from pathlib import Path
from typing import Literal

from pydantic import Field

from snow_today_webapp_ingest.types_.base import BaseModel, RootModel
from snow_today_webapp_ingest.types_.misc import NumericIdentifier, StringIdentifier

###############################################################################
# Types for region input things (e.g. magic strings in shapefiles)
###############################################################################

# The shapes for the regions come in shapefiles categorized thusly:
ShapefileCategory = Literal['HUC2', 'HUC4', 'State']


###############################################################################
# Types for region output things (e.g. magic strings, the JSON region index)
###############################################################################
VariableIdentifier = NumericIdentifier
RegionIdentifier = NumericIdentifier
SubRegionCollectionIdentifier = StringIdentifier


# NOTE: SuperRegion inherits from this class, careful about changes :)
class SubRegion(BaseModel):
    """A region that is not a super region.

    Must be a member of a SubRegionCollection.
    """

    long_name: str
    short_name: str
    shape_relative_path: Path


class SubRegionsIndex(RootModel):
    """An index, with numeric keys, of sub-region definitions."""

    root: dict[RegionIdentifier, SubRegion]


class SubRegionCollection(BaseModel):
    """A collection of sub-regions.

    This is only a definition of a collection, and does not include its relationships.
    See SubRegionsHierarchy for relationships.
    """

    long_name: str
    short_name: str


class SubRegionCollectionsIndex(RootModel):
    """An index, with numeric keys, of sub-region collection definitions."""

    root: dict[SubRegionCollectionIdentifier, SubRegionCollection]


class SuperRegionVariable(BaseModel):
    """A variable available in this super region."""

    default: bool = Field(
        description=(
            "Whether this variable is the default selection for the super region"
            " (IMPORTANT: there should only be default variable per super region)"
        ),
    )
    data_value_range: tuple[int, int] = Field(
        description="The range of data values that the colormap will span",
    )
    geotiff_relative_path: Path


class SuperRegion(SubRegion):
    """A large region representing a top-level choice in the web application.

    Sub-region choices will be presented depending on the super region choice.
    Coordinate reference system, water year, available variables, and more are defined
    at the super region level and inherited by sub-regions.
    """

    crs: str = Field(description="The coordinate reference system for this region")
    # TODO: Available basemap(s)
    water_year: int = Field(
        description="The current water year",
        ge=1900,
        le=3000,
    )
    water_year_start_date: dt.date = Field(
        description="The first day of the current water year"
    )
    historic_start_water_year: int = Field(
        description="The water year at the start of available climatology",
        ge=1900,
        le=3000,
    )
    last_date_with_data: dt.date
    historic_source: str = Field(description="The source of the climatology")
    sub_regions_relative_path: Path
    sub_regions_hierarchy_relative_path: Path
    variables: dict[VariableIdentifier, SuperRegionVariable] = Field(
        description="The variables available for this region",
    )


class SuperRegionsIndex(RootModel):
    """An index of Super Regions by numeric identifier."""

    root: dict[RegionIdentifier, SuperRegion]
