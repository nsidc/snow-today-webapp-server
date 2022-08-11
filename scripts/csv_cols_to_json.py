"""Convert CSV at stdin to JSON.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.
"""
import csv, json, math, sys


def _nan_to_none(val):
    if math.isnan(val):
        return None
    return val


def _normalize_value(dct, k):
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


if __name__ == '__main__':
    csv_as_list_of_dicts = [dict(r) for r in csv.DictReader(sys.stdin)]
    csv_as_dict_of_lists = {
        k: [_normalize_value(dct, k) for dct in csv_as_list_of_dicts]
        for k in csv_as_list_of_dicts[0].keys()
    }

    print(json.dumps(csv_as_dict_of_lists))
