"""Module for loading and saving data to various formats."""

import json


def save_dict_to_json(data, filename, **kwargs):
    """Save data to json file."""
    with open(file=filename, mode="w", encoding="utf-8") as fhandle:
        json.dump(data, fhandle, indent=6, **kwargs)


def read_json(path):
    """Reads json data to a python dict."""
    with open(file=path, mode="r", encoding="utf-8") as fhandle:
        data = json.load(fhandle)
    return data
