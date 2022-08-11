"""Convert CSV at stdin to JSON.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.
"""
import csv, json, sys


def _normalize_value(dct, k):
    """The "index" (doy) is integer, and the values are floats."""
    if k == 'day_of_water_year':
        return int(dct[k])
    else:
        return float(dct[k])


if __name__ == '__main__':
    csv_as_list_of_dicts = [dict(r) for r in csv.DictReader(sys.stdin)]
    csv_as_dict_of_lists = {
        k: [_normalize_value(dct, k) for dct in csv_as_list_of_dicts]
        for k in csv_as_list_of_dicts[0].keys()
    }

    print(json.dumps(
        csv_as_dict_of_lists,
        # Convert NaNs to nulls:
        ignore_nan=True,
    ))
