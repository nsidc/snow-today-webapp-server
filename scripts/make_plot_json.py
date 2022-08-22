"""Convert CSV plot files to JSON and write them to the storage location.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.

NOTE: These outputs should not be committed!
"""
import csv, io, json, math, os, sys
from pathlib import Path
from typing import Literal, TypedDict, get_args

try:
    STORAGE_DIR = Path(os.environ['STORAGE_DIR'])
    OUTPUT_DIR = Path(os.environ['SERVER_PLOTS_DIR'])
except Exception as e:
    raise RuntimeError(
        f'Expected $STORAGE_DIR and $SERVER_PLOTS_DIR envvars to be populated: {e}'
    )

INPUT_DIR = STORAGE_DIR / 'snow_today_2.0_testing' / 'linePlotsToDate'


class PlotDataPoint(TypedDict):
    day_of_water_year: int
    min: float
    prc25: float
    median: float
    prc75: float
    max: float
    year_to_date: float


Header = Literal[
    'day_of_water_year',
    'min',
    'prc25',
    'median',
    'prc75',
    'max',
    'year_to_date',
]
HEADERS = get_args(Header)


def _nan_to_none(val):
    if math.isnan(val):
        return None
    return val


def _normalize_value(dct: PlotDataPoint, k: Header):
    """The "index" (doy) is integer, and the values are floats.

    Also convert NaNs to None.
    """
    val = dct[k]
    if k == 'day_of_water_year':
        return int(val)
    else:
        float_val = float(val)

        # The Python JSON encoder outputs NaNs, which are _not_ valid JSON.
        # Convert to nulls:
        if math.isnan(float_val):
            return None

        return float_val


def cleanse_input(input_csv_fp: Path) -> list[str]:
    """Standardize header and remove trailer."""
    with open(input_csv_fp, 'r') as input_csv_file:
        input_csv = input_csv_file.readlines()

    # Replace header row with standard value
    header_row = ','.join(HEADERS)
    input_csv[0] = f'{header_row}\n'

    # Remove trailer (everything after blank line)
    index_of_blank_line = input_csv.index('\n')
    if index_of_blank_line != 367:
        raise RuntimeError(
            f'Blank line in {input_csv_fp} expected at line 367. Found at'
            f' {index_of_blank_line}.'
        )

    csv_rows = input_csv[0:index_of_blank_line]
    return csv_rows


def csv_cols_to_dict(csv_rows: list[str]) -> dict[Header, list]:
    csv_as_list_of_dicts = [
        dict(r)
        for r in csv.DictReader(io.StringIO(''.join(csv_rows)))
    ]
    csv_as_dict_of_lists = {
        k: [_normalize_value(dct, k)
            for dct in csv_as_list_of_dicts]
        for k in csv_as_list_of_dicts[0].keys()
    }
    return csv_as_dict_of_lists


def _variable_id_from_input_fn(input_fn: str) -> str:
    """SnowToday_USCO_SCF_WY2022_yearToDate.txt"""
    mapping = {
        'Albedo': 'albedo_observed_muZ',
        'RF': 'radiative_forcing',
        'SCF': 'snow_fraction',
        'SCD': 'snow_cover_days',
    }

    input_var = input_fn.split('_')[2]
    return mapping[input_var]


def _region_id_from_input_fn(input_fn: str) -> ...:
    """SnowToday_USCO_SCF_WY2022_yearToDate.txt"""
    # TODO: Support HUCs?
    input_region = input_fn.split('_')[1]
    state_id = input_region[2:4]

    return f'USwest_State_{state_id}'


def output_fp_from_input_fp(input_fp: Path) -> Path:
    input_fn = input_fp.name
    variable_id = _variable_id_from_input_fn(input_fn)
    region_id = _region_id_from_input_fn(input_fn)

    output_fn = f'{region_id}-{variable_id}.json'
    output_fp = OUTPUT_DIR / output_fn
    return output_fp


if __name__ == '__main__':
    for input_csv_fp in INPUT_DIR.glob('*.txt'):
        cleansed_csv_rows = cleanse_input(input_csv_fp)
        dict_of_cols = csv_cols_to_dict(''.join(cleansed_csv_rows))

        output_fp = output_fp_from_input_fp(input_csv_fp)

        with open(output_fp, 'w') as output_file:
            json.dump(dict_of_cols, output_file, indent=2)