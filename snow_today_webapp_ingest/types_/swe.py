import datetime as dt

from pydantic import BaseModel
from typing_extensions import TypedDict

from snow_today_webapp_ingest.types_.json import JsonMetadataAndData


class SweDataPoint(TypedDict):
    """A SWE station's data structure in the JSON output."""

    name: str
    lon: float
    lat: float
    elevation_meters: float
    swe_inches: float | None
    # SWE delta: current SWE - previous day's SWE
    swe_delta_inches: float | None
    # SWE normalized: current SWE / average SWE for this date of each year
    swe_normalized_pct: float | None


class SweMetadata(BaseModel):
    date: dt.date


SweJson = JsonMetadataAndData[SweMetadata, list[SweDataPoint]]
