"""Convert CSV Snow-Water Equivalent files to JSON and write them to disk.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.

NOTE: These outputs should not be committed!
"""
import csv
import io
import json
from typing import Literal, TypedDict, cast, get_args

import util.field_transformers as xfr
from constants.paths import INCOMING_SWE_DIR, STORAGE_POINTS_DIR
from loguru import logger
from util.csv import read_and_strip_before_header
from util.error import UnexpectedInput


class SweDataPoint(TypedDict):
    """A SWE station's data structure in the JSON output."""

    name: str
    lon: float
    lat: float
    elevation_meters: float
    swe_inches: float | None
    # SWE normalized: current SWE / average SWE for this date of each year
    swe_normalized_inches: float | None
    # SWE difference: current SWE - previous day's SWE
    swe_diff_inches: float | None
    state: str
    huc2: int | None
    huc4: int | None


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
    normalized = SweDataPoint(
        name=str.title(csv_dict['Name']),
        lon=float(csv_dict['Lon']),
        lat=float(csv_dict['Lat']),
        elevation_meters=float(csv_dict['Elev_m']),
        swe_inches=xfr.float_nan_normalized(csv_dict['SWE']),
        swe_normalized_inches=xfr.float_nan_normalized(csv_dict['normSWE']),
        swe_diff_inches=xfr.float_nan_normalized(csv_dict['dSWE']),
        state=xfr.state_normalized(csv_dict['State']),
        huc2=xfr.huc2_normalized(csv_dict['HUC02']),
        huc4=xfr.huc4_normalized(csv_dict['HUC04']),
    )
    return normalized


def normalize_csv_dicts(csv_dicts: list[CsvDict]) -> list[SweDataPoint]:
    normalized = [_normalize_csv_dict(d) for d in csv_dicts]
    ordered = sorted(normalized, key=lambda d: d['name'])
    return ordered


def csv_as_list_of_dicts(csv_text: str) -> list[CsvDict]:
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


def make_swe_json() -> None:
    input_files = list(INCOMING_SWE_DIR.glob('*.txt'))
    if len(input_files) != 1:
        raise UnexpectedInput(
            f'Expected 1 input file in {INCOMING_SWE_DIR}.' f' Got: {input_files}'
        )

    input_csv_fp = input_files[0]
    logger.info(f'Generating SWE JSON from: {input_csv_fp}...')

    header = ','.join(CSV_COLUMN_NAMES)
    csv_rows = read_and_strip_before_header(fp=input_csv_fp, header=header)
    csv_text = ''.join(csv_rows)

    csv_dicts = csv_as_list_of_dicts(csv_text)

    normalized = normalize_csv_dicts(csv_dicts)

    output_fp = STORAGE_POINTS_DIR / 'swe.json'
    with open(output_fp, 'w') as output_file:
        json.dump(normalized, output_file, indent=2, allow_nan=False)

    logger.info(f'SWE JSON written: {output_fp}')


if __name__ == '__main__':
    make_swe_json()
