"""Convert CSV plot files to JSON and write them to disk.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.

NOTE: These outputs should not be committed!
"""
import csv
import io
import json
import math
from pathlib import Path
from pprint import pformat
from typing import Literal, TypedDict, cast, get_args

from constants.paths import INCOMING_PLOT_CSV_DIR, STORAGE_PLOTS_DIR
from loguru import logger
from util.csv import read_and_strip_before_header
from util.region import make_region_code


class PlotDataPoint(TypedDict):
    day_of_water_year: int
    min: float
    prc25: float
    median: float
    prc75: float
    max: float
    year_to_date: float


ColumnName = Literal[
    'day_of_water_year',
    'min',
    'prc25',
    'median',
    'prc75',
    'max',
    'year_to_date',
]
COLUMN_NAMES = get_args(ColumnName)


def _normalize_value(dct: PlotDataPoint, k: ColumnName):
    """Normalize values to expected types.

    The "index" (doy) is integer, and all other columns are floats.

    `NaN`s are converted to `None` for JSON compliance (JSON doesn't support `None` or
    `NaN`. The Python `json.dumps` function will convert `None` to compliant value of
    `null`, but will not convert `NaN`!)
    """
    val = dct[k]
    if k == 'day_of_water_year':
        return int(val)
    else:
        float_val = float(val)

        # The Python JSON encoder outputs NaNs, which are invalid JSON numbers.
        if math.isnan(float_val):
            return None

        return float_val


def csv_to_dict_of_cols(csv_text: str) -> dict[ColumnName, list[float] | list[int]]:
    """Convert a string of CSV data to dict of lists."""
    csv_as_list_of_dicts = [
        # NOTE: I don't think we can get rid of this cast; Mypy can't know about the CSV
        # structure.
        cast(PlotDataPoint, dict(r))
        for r in csv.DictReader(io.StringIO(csv_text))
    ]

    # TODO: Can we get rid of this cast???
    csv_columns = cast(set[ColumnName], set(csv_as_list_of_dicts[0].keys()))
    csv_as_dict_of_lists = {
        k: [_normalize_value(dct, k) for dct in csv_as_list_of_dicts]
        for k in csv_columns
    }
    return csv_as_dict_of_lists


def _variable_id_from_input_fn(input_fn: str) -> str:
    """Extract variable identifier from input filename.

    e.g.:
        * SnowToday_USWY_radiative_forcing_WY2022_yearToDate.csv
                         ^^^^^^^^^^^^^^^^^
        * SnowToday_HUC12_snow_fraction_WY2022_yearToDate.csv
                          ^^^^^^^^^^^^^
        * SnowToday_USwest_albedo_observed_muZ_WY2022_yearToDate.csv
                           ^^^^^^^^^^^^^^^^^^^
    """
    # TODO: Consider a regex. Probably doesn't matter.
    input_var = input_fn.split('_')[2:-2]
    result = '_'.join(input_var)
    return result


def _region_id_from_input_fn(input_fn: str) -> str:
    """Derive output region ID from input filename.

    E.g.:
        * SnowToday_USWY_radiative_forcing_WY2022_yearToDate.csv
                    ^^^^ State: Wyoming
        * SnowToday_HUC12_snow_fraction_WY2022_yearToDate.csv
                    ^^^^^ HUC: 12
        * SnowToday_USwest_albedo_observed_muZ_WY2022_yearToDate.csv
                    ^^^^^^ Super-region: USwest
    """
    input_region = input_fn.split('_')[1]
    if input_region == 'USwest':
        return make_region_code('USwest')
    elif input_region.startswith('HUC'):
        huc_id = input_region[3:]
        return make_region_code('USwest', 'HUC', huc_id)
    elif len(input_region) == 4 and input_region.startswith('US'):
        state_id = input_region[2:4]
        return make_region_code('USwest', 'State', state_id)
    else:
        # TODO: HMA countries, basins
        raise NotImplementedError(f'Unexpected region in filename: {input_fn}')


def output_fp_from_input_fp(input_fp: Path, *, output_dir: Path) -> Path:
    input_fn = input_fp.name
    variable_id = _variable_id_from_input_fn(input_fn)
    region_id = _region_id_from_input_fn(input_fn)

    output_fn = f'{region_id}-{variable_id}.json'
    output_fp = output_dir / output_fn
    return output_fp


def make_plot_json() -> None:
    input_files = list(INCOMING_PLOT_CSV_DIR.glob('*.csv'))

    input_files_pretty = pformat([str(p) for p in input_files], indent=4)
    logger.info(f'Generating plot JSON from:\n{input_files_pretty}...')
    for input_csv_fp in input_files:
        # TODO: use new util
        header = ','.join(COLUMN_NAMES)
        csv_rows = read_and_strip_before_header(fp=input_csv_fp, header=header)
        csv_text = ''.join(csv_rows)

        dict_of_cols = csv_to_dict_of_cols(csv_text)

        output_fp = output_fp_from_input_fp(input_csv_fp, output_dir=STORAGE_PLOTS_DIR)
        with open(output_fp, 'w') as output_file:
            json.dump(dict_of_cols, output_file, indent=2)

    logger.info(f'Plot JSON written to {STORAGE_PLOTS_DIR}')


if __name__ == '__main__':
    make_plot_json()
