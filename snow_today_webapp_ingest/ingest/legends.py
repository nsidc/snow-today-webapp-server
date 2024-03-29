import json
from pathlib import Path

from loguru import logger

from snow_today_webapp_ingest.constants.paths import (
    REPO_STATIC_COLORMAPS_INDEX_FP,
    REPO_STATIC_SSP_VARIABLES_INDEX_FP,
)
from snow_today_webapp_ingest.util.legend import make_legend


def generate_swe_legends(
    from_path: Path,
    to_path: Path,
):
    """Generate legends based on SWE variable metadata."""
    variables_json: dict[str, dict] = json.loads(from_path.read_text())
    colormaps_json: dict[str, dict] = json.loads(
        REPO_STATIC_COLORMAPS_INDEX_FP.read_text()
    )

    for variable_id, variable_params in variables_json.items():
        output_fn = f"{variable_id}.svg"
        output_fp = to_path / output_fn

        colormap_id = variable_params["colormapId"]
        colormap = colormaps_json[str(colormap_id)]["colors"]

        to_path.mkdir(exist_ok=True, parents=True)
        make_legend(
            colormap=colormap,
            # This value range could be static every day, or it could change
            # day-by-day. For example, "snow cover days" variable has a colormap
            # that changes each day.
            colormap_value_range=tuple(variable_params["colormapValueRange"]),
            data_value_range=tuple(variable_params["valueRange"]),
            label=variable_params["labelMapLegend"],
            transparent_zero=variable_params["transparentZero"],
            output_fp=output_fp,
        )
        logger.info(f"Legend generated: {output_fp.name}")


def generate_ssp_legends(
    from_path: Path,
    to_path: Path,
):
    """Generate legends based on variable and super-region metadata."""
    # TODO: TYPES!!! We should use Pydantic to define types and generate JSON schemas
    #       from them.
    # TODO: Instead of using repo paths directly, they should be passed in as a dict to
    #       `from_path`.
    regions_json: dict[str, dict] = json.loads(from_path.read_text())
    variables_json: dict[str, dict] = json.loads(
        REPO_STATIC_SSP_VARIABLES_INDEX_FP.read_text()
    )
    colormaps_json: dict[str, dict] = json.loads(
        REPO_STATIC_COLORMAPS_INDEX_FP.read_text()
    )

    for region_id, region_params in regions_json.items():
        # NB: `region_variable_params` are the settings for a specific region-variable
        # relationship, e.g. a given region's default variable. `variable_params` is the
        # whole config for the variable, and is much larger.
        for variable_id, region_variable_params in region_params["variables"].items():
            variable_params = variables_json[str(variable_id)]

            # Only some types of variables get legends:
            layer_type = variable_params["layerType"]
            if layer_type not in ["raster", "point_swe"]:
                logger.debug(
                    f"Won't create legend for {variable_id=};"
                    f" {layer_type=} does not have legends."
                )
                continue

            colormap_id = variable_params["colormapId"]
            colormap = colormaps_json[str(colormap_id)]["colors"]

            output_fn = f"{region_id}_{variable_id}.svg"
            output_fp = to_path / output_fn

            to_path.mkdir(exist_ok=True, parents=True)
            make_legend(
                colormap=colormap,
                # This value range could be static every day, or it could change
                # day-by-day. For example, "snow cover days" variable has a colormap
                # that changes each day, and differs for each region.
                # TODO: This naming is very confusing. Fix it.
                colormap_value_range=tuple(region_variable_params["dataValueRange"]),
                data_value_range=tuple(variable_params["valueRange"]),
                label=variable_params["labelMapLegend"],
                transparent_zero=variable_params["transparentZero"],
                output_fp=output_fp,
            )
            logger.info(f"Legend generated: {output_fp.name}")
