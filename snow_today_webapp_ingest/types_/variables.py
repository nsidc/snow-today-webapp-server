from typing import Literal

from pydantic import Field

from snow_today_webapp_ingest.types_.base import BaseModel, RootModel
from snow_today_webapp_ingest.types_.misc import NumericIdentifier

VariableIdentifier = NumericIdentifier


class Variable(BaseModel):
    """A unique satellite variable (sensor, platform, algorithm)."""

    # These 3 together are the true unique identifiers of a variable
    sensor: str
    platform: str
    algorithm: str

    # TODO: Document!
    source: str
    layer_type: Literal["raster", "raster_notprocessed", "point_swe"] = Field(
        description=(
            "We have to differentiate between variables selectable for rasters/plots,"
            " for not processed layer, and for SWE, because they go to separate user"
            " interface elements. TODO: These things should be in separate files!"
        ),
    )
    long_name: str
    long_name_plot: str
    help_text: str
    label_map_legend: str
    label_plot_yaxis: str
    value_precision: int
    value_range: tuple[int, int] = Field(
        description="The range of values this variable can realistically have",
    )
    no_data_value: int
    colormap_id: int
    transparent_zero: bool


class VariablesIndex(RootModel):
    """Mapping of satellite variable unique IDs to properties."""

    root: dict[VariableIdentifier, Variable]
