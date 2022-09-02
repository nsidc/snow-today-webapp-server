"""Convert CSV plot files to JSON and write them to the storage location.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.

NOTE: These outputs should not be committed!
"""
import csv
import io
import json
import math
from pathlib import Path
from typing import Literal, TypedDict, cast, get_args

from util.env import env_get
from util.region import make_region_code


STORAGE_DIR = Path(env_get('STORAGE_DIR'))
OUTPUT_DIR = Path(env_get('SERVER_PLOTS_DIR'))

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


def cleanse_input(input_csv_fp: Path) -> list[str]:
    """Strip metadata in the first 11 lines of the CSV file.

    NOTE: In the future, this metadata may be useful!
    """
    EXPECTED_BLANK_LINE = 11

    with open(input_csv_fp, 'r') as input_csv_file:
        input_csv = input_csv_file.readlines()

    # Replace header row with standard value
    header_row = ','.join(HEADERS)
    input_csv[0] = f'{header_row}\n'

    # Find the blank line; everything above that is metadata
    # NOTE: We add 1 because to humans, line numbers start with 1, and list indexes
    # start at 0.
    blank_line_number = input_csv.index('\n') + 1
    if blank_line_number != EXPECTED_BLANK_LINE:
        raise RuntimeError(
            f'Blank line in {input_csv_fp} expected at line {EXPECTED_BLANK_LINE}.'
            f' Found at: {blank_line_number}.'
        )

    # Remove metadata (everything above blank line)
    # NOTE: Remember that `blank_line_number` was incremented by 1 above to represent
    # the human-readable line number. Since we don't want the blank line number to be
    # included in the output, that's a good thing; a slice includes the "start" value,
    # and we only want the lines _after, but not including_ the blank line.
    csv_rows = input_csv[blank_line_number:]
    return csv_rows


def csv_cols_to_dict(csv_rows: str) -> dict[Header, list[float] | list[int]]:
    """Convert a string of CSV data to dict of lists."""
    csv_as_list_of_dicts = [
        # NOTE: I don't think we can get rid of this cast; Mypy can't know about the CSV
        # structure.
        cast(PlotDataPoint, dict(r))
        for r in csv.DictReader(io.StringIO(''.join(csv_rows)))
    ]

    # TODO: Can we get rid of this cast???
    csv_columns = cast(set[Header], set(csv_as_list_of_dicts[0].keys()))
    csv_as_dict_of_lists = {
        k: [
            _normalize_value(dct, k)
            for dct in csv_as_list_of_dicts
        ]
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


def output_fp_from_input_fp(input_fp: Path) -> Path:
    input_fn = input_fp.name
    variable_id = _variable_id_from_input_fn(input_fn)
    region_id = _region_id_from_input_fn(input_fn)

    output_fn = f'{region_id}-{variable_id}.json'
    output_fp = OUTPUT_DIR / output_fn
    return output_fp


if __name__ == '__main__':
    input_files = list(INPUT_DIR.glob('*.csv'))
    for input_csv_fp in input_files:
        cleansed_csv_rows = cleanse_input(input_csv_fp)
        dict_of_cols = csv_cols_to_dict(''.join(cleansed_csv_rows))

        output_fp = output_fp_from_input_fp(input_csv_fp)

        with open(output_fp, 'w') as output_file:
            json.dump(dict_of_cols, output_file, indent=2)
