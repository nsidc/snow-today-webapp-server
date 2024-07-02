import datetime as dt
from typing import Annotated

from annotated_types import Ge, Le, MaxLen, MinLen
from pydantic import Field

from snow_today_webapp_ingest.types_.base import BaseModel
from snow_today_webapp_ingest.types_.json import JsonMetadataAndData

DESCRIPTION_TEMPLATE = (
    "The water year in which the average (depending on the variable, could be median,"
    " mean, or sum) of all days in the water year represents a historical {STATISTIC}"
    " for this region and variable."
)
# TODO: When Mypy supports PEP695 (https://github.com/python/mypy/issues/15238), do:
#     PlotColumn[T] = Annotated[list[T], MinLen(1), MaxLen(366)]
# Or use TypeVar + TypeAlias until then? Does that work??
#     _T = TypeVar("_T")
#     PlotColumn: TypeAlias = Annotated[list[T], MinLen(1), MaxLen(366)]
PlotDoyValue = Annotated[int, Ge(1), Le(366)]
PlotDoyColumn = Annotated[list[PlotDoyValue], MinLen(1), MaxLen(366)]
PlotPointValue = float | None
PlotPointColumn = Annotated[list[PlotPointValue], MinLen(1), MaxLen(366)]


class PlotMetadata(BaseModel):
    min_year: int = Field(
        description=DESCRIPTION_TEMPLATE.format(STATISTIC="minimum"),
        ge=1900,
        le=3000,
    )
    max_year: int = Field(
        description=DESCRIPTION_TEMPLATE.format(STATISTIC="maximum"),
        ge=1900,
        le=3000,
    )


class PlotData(BaseModel):
    """A mapping of column headers to arrays of column values.

    It's expected that each array will be the same length.
    """

    day_of_water_year: PlotDoyColumn = Field(
        description="The day of water year for this row, starting with 1",
    )
    date: list[dt.date] = Field(
        description="The calendar date (YYYY-MM-DD) for this row",
    )
    year_to_date: PlotPointColumn = Field(
        description="Observed values for the current water year to date",
    )
    min: PlotPointColumn = Field(
        description=(
            "Observed values for the minimum water year (as specified in"
            " `metadata.minYear`)"
        ),
    )
    max: PlotPointColumn = Field(
        description=(
            "Observed values for the maximum water year (as specified in"
            " `metadata.maxYear`)"
        ),
    )
    median: PlotPointColumn = Field(
        description="Historical median for each day of the water year",
    )
    prc25: PlotPointColumn = Field(
        description="Historical 25th percentile for each day of the water year",
    )
    prc75: PlotPointColumn = Field(
        description="Historical 75th percentile for each day of the water year",
    )


# TODO: Better suffix than Payload... Data isn't appropriate, because metadata also
#       included. But we're using the term "Data" to refer to e.g. SWE, Plots, COGs, ...
# TODO: Description: "Daily plot data and metadata for a specific region ID and variable
# ID (found in filename by convention)."
PlotPayload = JsonMetadataAndData[PlotMetadata, PlotData]
