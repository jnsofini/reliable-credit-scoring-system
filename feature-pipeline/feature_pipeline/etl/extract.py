"""
Pulls data from the web
"""
import datetime
from json import JSONDecodeError
from typing import Any, Dict, Tuple, Optional, List, Union
import pandas as pd
import requests
from feature_pipeline import utils


# logger = utils.get_logger(__name__)

def get_data_url(url: str) -> Optional[Tuple[pd.DataFrame, Dict[str, Any]]]:
    """
    Extract data from NYC cloudflare link.

    Args:
        export_end_reference_datetime: The end reference datetime of the export window. If None, the current time is used.
            Because the data is always delayed with "days_delay" days, this date is used only as a reference point.
            The real extracted window will be computed as [export_end_reference_datetime - days_delay - days_export, export_end_reference_datetime - days_delay].
        days_delay: Data has a delay of N days. Thus, we have to shift our window with N days.
        days_export: The number of days to export.
        url: The URL of the API.

    Returns:
          A tuple of a Pandas DataFrame containing the exported data and a dictionary of metadata.
    """
    # if urls and not isinstance(urls, list):
    #     urls = list(urls)


    #logger.info(f"Requesting data from API with URL: {url}")
    records = pd.read_parquet(url)
    #logger.info(f"Response received from API with status code: {response.status_code} ")


    # Prepare metadata.
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    metadata = {
        "url": url,
        "dataload_date": datetime.datetime.utcnow().replace(
            minute=0, second=0, microsecond=0
        ).strftime(datetime_format),
        "datetime_format": datetime_format,
    }

    return records, metadata

    
if __name__ == "__main__":

    GREEN_TAXI = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-01.parquet"

    records, metadata = get_data_url(GREEN_TAXI)

    print(metadata)
