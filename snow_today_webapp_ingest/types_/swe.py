import datetime as dt

from snow_today_webapp_ingest.types_.base import BaseModel
from snow_today_webapp_ingest.types_.json import JsonMetadataAndData


class SweDataPoint(BaseModel):
    """A SWE station's data structure in the JSON output."""

    name: str
    lon: float
    lat: float
    elevation_meters: float
    swe_inches: float | None
    swe_cm: float | None
    # SWE delta: current SWE - previous day's SWE
    swe_delta_inches: float | None
    swe_delta_cm: float | None
    # SWE normalized: current SWE / average SWE for this date of each year
    swe_normalized_pct: float | None
    # SWE max pct: Current SWE / max SWE for this date of each year
    swe_max_pct: float | None


class SweMetadata(BaseModel):
    last_date_with_data: dt.date


# TODO: Better name. Data isn't appropriate, because metadata also included. But we're
# using the term "Data" to refer to e.g. SWE, Plots, COGs, ...
# TODO: Description
SwePayload = JsonMetadataAndData[SweMetadata, list[SweDataPoint]]
