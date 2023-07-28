import json


def save_dict_to_json(data, filename, **kwargs):
    with open(file=filename, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=6, **kwargs)


def read_json(path):
    with open(file=path, mode="r", encoding="utf-8") as fhandle:
        data = json.load(fhandle)
    return data
