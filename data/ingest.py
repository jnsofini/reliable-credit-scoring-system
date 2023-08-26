"""Downloads FICO HELOC data from the many githud links."""
from pathlib import Path

import pandas as pd

DIR = Path(__file__).parent

URL = (
    "https://raw.githubusercontent.com/seanchen7/FICO-HELOC/master/heloc_dataset_v1.csv"
)


def download():
    """Download a csv from a link"""
    print(f"Downloading data from {URL}")
    data = pd.read_csv(URL)
    save_path = DIR / "raw-data.parquet"
    data.to_parquet(path=save_path)
    print(f"Data saved to {save_path}")


if __name__ == "__main__":
    download()
