from types_.regions import SubRegionCollectionName, SuperRegionName


def make_region_code(
    super_region_name: SuperRegionName,
    sub_region_collection_name: SubRegionCollectionName | None = None,
    sub_region_name: str | None = None,
    /,
) -> str:
    if sub_region_collection_name is None and sub_region_name is None:
        return super_region_name

    if sub_region_collection_name is None or sub_region_name is None:
        raise RuntimeError(
            'Sub-region collection and sub-region must both be passed, or both omitted.'
        )

    return f'{super_region_name}_{sub_region_collection_name}_{sub_region_name}'
