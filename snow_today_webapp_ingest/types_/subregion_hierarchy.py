from snow_today_webapp_ingest.types_.base import BaseModel, RootModel
from snow_today_webapp_ingest.types_.regions import (
    RegionIdentifier,
    SubRegionCollectionIdentifier,
)

# from snow_today_webapp_ingest.types_.omissible import Omissible


class SubRegionsHierarchyCollectionRegionsIndex(RootModel):
    """A mapping of sub-regions in a collection."""

    root: dict[RegionIdentifier, "SubRegionsHierarchyCollectionRegion"]


class SubRegionsHierarchyCollectionRegion(BaseModel):
    # TODO: Will this output as {} or null?
    collections: None | dict[
        SubRegionCollectionIdentifier,
        SubRegionsHierarchyCollectionRegionsIndex,
    ] = None


class SubRegionsHierarchyCollection(BaseModel):
    """A collection of sub-regions."""

    regions: SubRegionsHierarchyCollectionRegionsIndex


class SubRegionsHierarchyCollectionsIndex(RootModel):
    """Collections of sub-regions identified by a unique string ID, e.g. 'huc4'."""

    root: dict[SubRegionCollectionIdentifier, SubRegionsHierarchyCollection]


class SubRegionsHierarchy(BaseModel):
    """Hierarchy of sub-region collections and their members.

    Collections contain sub-regions, and sub-regions may themselves contain more
    collections. This can continue arbitrarily deep, but for user experience reasons,
    should be kept reasonable.
    """

    collections: SubRegionsHierarchyCollectionsIndex
