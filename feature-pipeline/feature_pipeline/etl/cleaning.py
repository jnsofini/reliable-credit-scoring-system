import pandas as pd
from typing import Dict, List

COLUMNS_RENAME = {
    "tpep_pickup_datetime": "pickup_time",
    "tpep_dropoff_datetime": "dropoff_time",
    "improvement_surcharge": "improvement_charge",
    "congestion_surcharge": "congestion_charge",
    "store_and_fwd_flag": "store_flag"
}
# TODO: Add more types
COLUMNS_TYPES = {
    "pickup_time": "datetime[64]",
    "dropoff_time": "datetime[64]",
    "payment_tyme": "int8"
}


MODELLING_COLUMNS = ['pulocationid', 'dolocationid', 'duration']

def rename_columns(df: pd.DataFrame, columns: Dict[str, str] = COLUMNS_RENAME) -> pd.DataFrame:
    """
    Rename columns to match our schema.
    """

    data = df.drop(                       # Drop irrelevant columns.
        columns=["VendorID", "RatecodeID"]
        ).rename(                           # Rename columns
        columns=COLUMNS_RENAME
    ) # Return a copy

    data.columns = data.columns.str.lower()

    return data


def cast_columns(df: pd.DataFrame, columns_type: Dict[str, str]) -> pd.DataFrame:
    """
    Cast columns to the correct data type.
    """

    data = df.astype(columns_type)

    return data



def add_trip_duration(
    df: pd.DataFrame,
    pick_up_time: str = "tpep_pickup_datetime",
    drop_off_time: str = "tpep_dropoff_datetime",
) -> pd.DataFrame:
    """Adds the column `duration` to the DataFrame.

    The column duration is derived from the pickup and drop off time stamps.

    Args:
        df (pd.DataFrame): Raw data of the taxi trip data
        pick_up_time (str, optional): The pickup time. Defaults to "tpep_pickup_datetime".
        drop_off_time (str, optional): Dropoff time. Defaults to "tpep_dropoff_datetime".

    Returns:
        pd.DataFrame: The taxi data with duration added
    """
    df[pick_up_time] = pd.to_datetime(df[pick_up_time])
    df[drop_off_time] = pd.to_datetime(df[drop_off_time])
    df = df.assign(
        duration=df[drop_off_time] - df[pick_up_time]
        )
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    return df


def remove_outliers(
    df: pd.DataFrame, strategy: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """Removes outliers defined as a strategy.

    The strategy is defined as the a dict with columns as keys and the key is another dict
    with keys min and max whose values depict the cutoff of the outliers

    Args:
        df (pd.DataFrame): DataFrame with outliers present.
        strategy (Dict[str, Dict[str, float]]): The strategy to remove outliers

    Returns:
        pd.DataFrame: The processed data with ourliers removed.
    """
    # mask = pd.Series(df.shape[0]*[True])

    for column, outlier in strategy.items():
        # TODO: Make the following mask to only run on series and filter outside the loop
        # print(column, outlier)
        mask = (df[column] >= outlier.get("min", df[column].min())) & (
            df[column] <= outlier.get("max", df[column].max())
        )
        # print(mask)
        df = df[mask]

    return df


def categorial_feature_prepocessing(
    df: pd.DataFrame, categorical_features: List[str]
) -> pd.DataFrame:
    """Preprocess categorical features.

    Here we simply preprocess them by casting them as strings.

    Args:
        df (pd.DataFrame): Data with both numerical and categorical columns
        categorical_features (List[str]): List of ategorical feature

    Returns:
        pd.DataFrame: Process dataframe
    """
    df[categorical_features] = df[categorical_features].astype(str)

    return df


def preprocess_taxi_data(
    df: pd.DataFrame,
    pickup_dropoff: Dict[str, str],
    strategy: Dict[str, Dict[str, float]],
    categorical_features: List[str],
) -> pd.DataFrame:
    """Adds duration data using `add_trip_duration` and removes outliers using `remove_outliers.`

    Args:
        df (pd.DataFrame): DataFrame with outliers present.
        strategy (Dict[str, Dict[str, float]]): The strategy to remove outliers
        categorical_features (List[str]): List of categorical features to pass to categoricla feature processing

    Returns:
        pd.DataFrame: The processed data with ourliers removed.
    """
    print(df.columns)
    if not "duration" in df.columns:
        df = add_trip_duration(
            df=df,
            pick_up_time=pickup_dropoff["pickup"],
            drop_off_time=pickup_dropoff["dropoff"],
        )
    df = remove_outliers(df=df, strategy=strategy)
    df = categorial_feature_prepocessing(
        df, categorical_features=categorical_features
    )

    return df
