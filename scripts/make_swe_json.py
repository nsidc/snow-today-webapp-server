"""Convert CSV Snow-Water Equivalent files to JSON and write them to disk.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.

NOTE: These outputs should not be committed!
"""
import csv
import io
import json
import math
from pathlib import Path
from typing import Callable, Literal, TypedDict, cast, get_args

from loguru import logger

import util.field_transformers as xfr
from constants.paths import INCOMING_SWE_DIR, STORAGE_POINTS_DIR
from util.csv import read_and_strip_before_header
from util.error import UnexpectedInput


# The JSON data won't be in "column" orientation; these strings simply correspond with
# the CSV columns.
# TODO: Extract types to another module or stub file
JsonColumnName = Literal[
    'name',
    'lat',
    'lon',
    'elevation_meters',
    'swe_inches',
    'swe_normalized_inches',
    'swe_diff_inches',
    'state',
    'huc2',
    'huc4',
]


class SweDataPoint(TypedDict):
    """A SWE station's data structure in the JSON output."""
    name: str
    lat: float
    lon: float
    elevation_meters: float
    swe_inches: float
    # SWE normalized: current SWE / average SWE for this date of each year
    swe_normalized_inches: float
    # SWE difference: current SWE - previous day's SWE
    swe_diff_inches: float
    state: str
    huc2: int | None
    huc4: int | None


class ColumnInfo(TypedDict):
    new_name: JsonColumnName 
    transformer: xfr.Transformer | None


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
CSV_COLUMNS: dict[CsvColumnName, ColumnInfo] = {
    'Name': {'new_name': 'name', 'transformer': str.title},
    'Lat': {'new_name': 'lat', 'transformer': None},
    'Lon': {'new_name': 'lon', 'transformer': None},
    'Elev_m': {'new_name': 'elevation_meters', 'transformer': None},
    'SWE': {'new_name': 'swe_inches', 'transformer': None},
    'normSWE': {'new_name': 'swe_normalized_inches', 'transformer': None},
    'dSWE': {'new_name': 'swe_diff_inches', 'transformer': None},
    'State': {'new_name': 'state', 'transformer': xfr.state_normalized},
    'HUC02': {'new_name': 'huc2', 'transformer': xfr.huc2_normalized},
    'HUC04': {'new_name': 'huc4', 'transformer': xfr.huc4_normalized},
}
CSV_COLUMN_NAMES = get_args(CsvColumnName)
JSON_COLUMN_NAMES = get_args(JsonColumnName)
CsvDict = dict[CsvColumnName, str | float]


def _normalize_csv_dict(csv_dict: CsvDict) -> SweDataPoint:
    normalized = {
        CSV_COLUMNS[column]['new_name']: xfr.transform_value(
            value=value,
            transformer=CSV_COLUMNS[column]['transformer'],
        )
        for column, value in csv_dict.items()
    }
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
            f'Expected 1 input file in {INCOMING_SWE_DIR}.'
            f' Got: {input_files}'
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
        json.dump(normalized, output_file, indent=2)

    logger.info(f'SWE JSON written: {output_fp}')


if __name__ == '__main__':
    make_swe_json()
