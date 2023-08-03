# pylint: disable=[missing-module-docstring,invalid-name,
# broad-exception-caught, logging-fstring-interpolation,fixme]
import datetime
import uuid
from typing import Dict, List

import numpy as np
import pandas as pd


def get_columns_types(df: pd.DataFrame, exemption=None) -> Dict[str, str]:
    """Gets the columns types."""
    if exemption is None:
        exemption = ["operation_date", "id", "RiskPerformance"]
    columns_types = {
        column: "int32" for column in df.columns if column not in exemption
    }
    columns_types["id"] = "str"

    return columns_types


def rename_columns(
    df: pd.DataFrame, columns: Dict[str, str] | None = None
) -> pd.DataFrame:
    """
    Rename columns to match our schema.
    """

    if columns is not None:
        df = df.rename(columns=columns)  # Rename columns  # Return a copy

    df.columns = df.columns.str.lower()

    return df


def add_date(data: pd.DataFrame) -> None:
    """Adds a date column called 'operation_date' to the dataframe.

    Our original data didn't have a date. We added this date to make the data
    richer and suitable for the project.

    Args:
        data (pd.DataFrame): The data without date column
    """
    data["operation_date"] = [
        datetime.date(2023, month, 1)
        for month in np.random.randint(1, 9, size=data.shape[0])
    ]


def add_ids(data: pd.DataFrame) -> None:
    """Adds a date column called 'is' to the dataframe

    Our original data didn't have a primary key.
    We added the 'id' ciolumn to make the data
    richer and suitable for the project.

    Args:
        data (pd.DataFrame): The data without a primary column
    """
    data["id"] = [uuid.uuid4() for _ in range(data.shape[0])]


def replace(df: pd.DataFrame, replacement: Dict[str, dict]) -> pd.DataFrame:
    """Takes a dataframe and replace values in columns with values provided.

    Args:
        df (pd.DataFrame): Dataframe which carries multiple columns
        replacement (dict): Dict with keys the string name and values
        dict of values to replace as keys and replament as values.

    Returns:
        pd.DataFrame: Dataframe with updated values
    """
    return df.replace(to_replace=replacement)


def cast_columns(df: pd.DataFrame, columns_type: Dict[str, str]) -> pd.DataFrame:
    """Cast columns to the correct data type.

    Args:
        df (pd.DataFrame): Dataframe which carries multiple columns
        columns_type (dict): Dict with keys the column name and values
        a string representation of the type.

    Returns:
        pd.DataFrame: Dataframe with updated values
    """

    data = df.astype(columns_type)

    return data


def remove_outliers(
    df: pd.DataFrame, strategy: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """Removes outliers defined as a strategy.

    The strategy is defined as the a dict with columns as
    keys and the key is another dict with keys min and max
    whose values depict the cutoff of the outliers

    Args:
        df (pd.DataFrame): DataFrame with outliers present.
        strategy (Dict[str, Dict[str, float]]): The strategy to remove outliers

    Returns:
        pd.DataFrame: The processed data with ourliers removed.
    """
    # mask = pd.Series(df.shape[0]*[True])

    for column, outlier in strategy.items():
        # Improve: Make the following mask to only run on series and
        # filter outside the loop
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
