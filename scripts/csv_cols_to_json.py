import csv, json, sys

csv_as_list_of_dicts = [dict(r) for r in csv.DictReader(sys.stdin)]
csv_as_dict_of_lists = {
    k: [dct[k] for dct in csv_as_list_of_dicts] for k in csv_as_list_of_dicts[0]
}

print(json.dumps(csv_as_dict_of_lists))
