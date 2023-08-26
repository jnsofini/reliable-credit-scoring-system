"""
Pulls data from the web.

We will update this later
"""
import pandas as pd
import uuid
import datetime

def get_data(path, ext="parquet"):
    """Reads data from path, add a unique id"""
    if path.endswith("csv"):
        raw_data = pd.read_csv(path)
    else:
        raw_data = pd.read_parquet(path)

    data = add_columns(raw_data)

    return data

def add_columns(data):
    data['operation_date'] = datetime.datetime.now().strftime("%m/%d/%Y")
    data['id'] = [str(uuid.uuid4()) for _ in range(data.shape[0])]
    return data
