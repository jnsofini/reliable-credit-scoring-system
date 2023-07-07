"""
Pulls data from the web.

We will update this later
"""
import pandas as pd

def get_data(path):
    return pd.read_parquet(path)
