from types_.regions import SubRegionCollectionName, SuperRegionName


def make_region_code(
    super_region_name: SuperRegionName,
    sub_region_collection_name: SubRegionCollectionName,
    sub_region_name: str,
) -> str:
    return f'{super_region_name}_{sub_region_collection_name}_{sub_region_name}'
