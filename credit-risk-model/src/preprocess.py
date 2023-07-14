"""
Preprocessing of data.

This script performs the preprocessing of the data used to build the model.
"""
import os
import time
import warnings

import config
import pandas as pd
from util import setup_binning

from sklearn.feature_selection import VarianceThreshold


warnings.filterwarnings("ignore", category=DeprecationWarning)

TARGET: str = "RiskPerformance"
SAVE_BINNING_OBJ = True
QUARTER_TO_REMOVE: str = "2016-3-31"
INCLUDE_FINANCIALS: bool = False

DATA_DIR = "data"


BINNING_FIT_PARAMS = {
    "ExternalRiskEstimate": {"monotonic_trend": "descending"},
    "MSinceOldestTradeOpen": {"monotonic_trend": "descending"},
    "MSinceMostRecentTradeOpen": {"monotonic_trend": "descending"},
    "AverageMInFile": {"monotonic_trend": "descending"},
    "NumSatisfactoryTrades": {"monotonic_trend": "descending"},
    "NumTrades60Ever2DerogPubRec": {"monotonic_trend": "ascending"},
    "NumTrades90Ever2DerogPubRec": {"monotonic_trend": "ascending"},
    "PercentTradesNeverDelq": {"monotonic_trend": "descending"},
    "MSinceMostRecentDelq": {"monotonic_trend": "descending"},
    "NumTradesOpeninLast12M": {"monotonic_trend": "ascending"},
    "MSinceMostRecentInqexcl7days": {"monotonic_trend": "descending"},
    "NumInqLast6M": {"monotonic_trend": "ascending"},
    "NumInqLast6Mexcl7days": {"monotonic_trend": "ascending"},
    "NetFractionRevolvingBurden": {"monotonic_trend": "ascending"},
    "NetFractionInstallBurden": {"monotonic_trend": "ascending"},
    "NumBank2NatlTradesWHighUtilization": {"monotonic_trend": "ascending"},
}

def _remove_feature(df: pd.DataFrame, columns_to_drop: str | list[str] | None = None):
    if columns_to_drop is None:
        return df
    if isinstance(columns_to_drop, str):
        columns_to_drop = [columns_to_drop]

    columns_to_drop = list(
        set(columns_to_drop).intersection(
        set(df.columns.values)
        )
        )
    return df.drop(columns=columns_to_drop)


def remove_feature_with_low_variance(df):
    var_reductor = VarianceThreshold()
    data_ = var_reductor.fit_transform(df)
    return data_


def load_data(path, drop_cols=None):
    df = pd.read_parquet(path)
    if drop_cols:
        columns_to_drop = list(set(drop_cols).intersection(set(df.columns.values)))
        return df.drop(columns=columns_to_drop)
    return df


def main(use_manual_bins=True):
    print("===========================================================")
    print("==================Preprocessing============================")
    print("===========================================================")
    start_time = time.perf_counter()

    # Get raw data and split into X and y

    X_train = load_data(path=os.path.join(DATA_DIR, "X_train.parquet"))
    y_train = pd.read_parquet(path=os.path.join(DATA_DIR, "y_train.parquet"))

    print("Using automatic bins")
    features_ = [col for col in X_train.columns if X_train[col].nunique() > 1]
    # Log removed columns

    X = X_train[features_]
    y = y_train.astype("int8").values.reshape(-1)

    binning_process = setup_binning(X, binning_fit_params=BINNING_FIT_PARAMS)
    binning_process.fit(X, y)

    # save binning table
    iv_table_name = "manual_iv_table" if use_manual_bins else "auto_iv_table"
    auto_iv_table = binning_process.summary()
    os.makedirs(path := os.path.join(DATA_DIR, "artifacts"), exist_ok=True)
    auto_iv_table.to_csv(os.path.join(path, f"{iv_table_name}.csv"))

    # Save Tranform data and binning_process
    X_transformed = binning_process.transform(X)
    X_transformed[TARGET] = y
    # print(X_transformed.head())
    X_transformed.to_parquet(os.path.join(path, config.TRANSFORM_DATA_PATH))

    if SAVE_BINNING_OBJ:
        binning_process.save(os.path.join(path, config.BINNING_TRANSFORM_PATH))

    print(f"Time taken : {round(time.perf_counter() - start_time, 2)} seconds")


if __name__ == "__main__":
    main()
