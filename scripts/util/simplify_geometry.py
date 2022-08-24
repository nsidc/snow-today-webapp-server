import geopandas as gpd


# The coefficient used to calculate the simplification threshold (by multiplying this
# number by the size of the shortest dimension of each shape's bbox). Smaller numbers
# result in finer output resolution.
# At .001, our biggest regions are 125KB. 7.2MB in total.
# At .0005, our biggest regions are 237KB. 13MB in total.
# At .0001, our biggest regions are 762KB. 41MB in total.
SIMPLIFICATION_COEFFICIENT = .0005


def simplify_geometry(feature_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
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
