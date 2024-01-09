"""Convert CSV Snow-Water Equivalent files to JSON and write them to disk.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.

CRITICAL: This code currently only expects and handles a single region of SWE data.
"""
import csv
import io
from pathlib import Path
from typing import Literal, cast, get_args

import yaml
from loguru import logger

import snow_today_webapp_ingest.util.field_transformers as xfr
from snow_today_webapp_ingest.types_.swe import SweDataPoint, SweMetadata, SwePayload
from snow_today_webapp_ingest.util.csv import read_csv_and_strip_before_header
from snow_today_webapp_ingest.util.error import UnexpectedInputError

CsvColumnName = Literal[
    'Name',
    'Lat',
    'Lon',
    'Elev_m',
    'SWE',
    'normSWE',
    'dSWE',
    'State',
    'HUC02',
    'HUC04',
]
CSV_COLUMN_NAMES = get_args(CsvColumnName)
CsvDict = dict[CsvColumnName, str]


def _normalize_csv_dict(csv_dict: CsvDict) -> SweDataPoint:
    """Make a standard object from CSV data.

    Some fields are dropped.
    """
    normalized = SweDataPoint(
        name=str.title(csv_dict['Name']),
        lon=float(csv_dict['Lon']),
        lat=float(csv_dict['Lat']),
        elevation_meters=float(csv_dict['Elev_m']),
        swe_inches=xfr.float_nan_normalized(csv_dict['SWE']),
        swe_normalized_pct=xfr.float_nan_normalized(csv_dict['normSWE']),
        swe_delta_inches=xfr.float_nan_normalized(csv_dict['dSWE']),
    )
    return normalized


def _normalize_csv_dicts(csv_dicts: list[CsvDict]) -> list[SweDataPoint]:
    normalized = [_normalize_csv_dict(d) for d in csv_dicts]
    ordered = sorted(normalized, key=lambda d: d.name)
    return ordered


def _csv_as_list_of_dicts(csv_text: str) -> list[CsvDict]:
    """Convert a string of CSV data to list of dicts."""
    list_of_dicts = [
        # NOTE: I don't think we can get rid of this cast; Mypy can't know about the CSV
        # structure.
        cast(CsvDict, dict(r))
        for r in csv.DictReader(
            io.StringIO(csv_text),
        )
    ]
    return list_of_dicts


def _normalize_metadata(metadata: str) -> SweMetadata:
    """Read the SWE CSV metadata header, which coincidentally is readable as YAML."""
    metadata_dict = yaml.safe_load(metadata)

    return SweMetadata(
        last_date_with_data=metadata_dict["SnowToday Calculated SWE Summary Data"],
    )


def ingest_swe_json(
    from_path: Path,
    to_path: Path,
) -> None:
    """Convert SWE CSV to JSON."""
    input_files = list(from_path.glob('*.txt'))
    if len(input_files) != 1:
        raise UnexpectedInputError(
            f'Expected 1 input file in {from_path}. Got: {input_files}'
        )

    input_csv_fp = input_files[0]
    logger.info(f"Generating SWE JSON from '{input_csv_fp}'...")

    header = ','.join(CSV_COLUMN_NAMES)
    # TODO: Read header metadata
    csv_text, stripped_text = read_csv_and_strip_before_header(
        fp=input_csv_fp,
        header=header,
    )

    csv_dicts = _csv_as_list_of_dicts(csv_text)

    output = SwePayload(
        metadata=_normalize_metadata(stripped_text),
        data=_normalize_csv_dicts(csv_dicts),
    )

    output_fp = to_path / 'swe.json'
    output_fp.parent.mkdir(parents=True, exist_ok=True)
    output_fp.write_text(output.model_dump_json())

    logger.success(f'SWE JSON written: {output_fp}')
