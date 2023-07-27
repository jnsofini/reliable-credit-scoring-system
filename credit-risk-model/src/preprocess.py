"""
Preprocessing of data.

This script performs the preprocessing of the data used to build the model.

python -m src.preprocess
"""
import logging
import os
import time
import warnings
import json
from pathlib import Path
from dataclasses import dataclass

# from src import config
from src.tools import timeit, stage_info, read_json, save_dict_to_json
import pandas as pd
from optbinning import BinningProcess
from sklearn.feature_selection import VarianceThreshold

# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(
    format='%(levelname)s:%(message)s', encoding='utf-8', level=logging.DEBUG
)

warnings.filterwarnings("ignore", category=DeprecationWarning)

TARGET: str = "RiskPerformance"
SAVE_BINNING_OBJ = True
BINNING_TRANSFORM_PATH = "binning-transformer.pkl"
TRANSFORM_DATA_PATH = "transform-data.parquet"
SPECIAL_CODES = [-9, -8, -7]
MISSING = [-99_000_000]

DATA_DIR = "data"
STAGE = "preprocessing"
test_dir = 'dev-test'
# dest_dir = Path(DATA_DIR).joinpath(test_dir, STAGE)

FILE_DIR = Path(__file__).parent

# BINNING_FIT_PARAMS = {
#     "ExternalRiskEstimate": {"monotonic_trend": "descending"},
#     "MSinceOldestTradeOpen": {"monotonic_trend": "descending"},
#     "MSinceMostRecentTradeOpen": {"monotonic_trend": "descending"},
#     "AverageMInFile": {"monotonic_trend": "descending"},
#     "NumSatisfactoryTrades": {"monotonic_trend": "descending"},
#     "NumTrades60Ever2DerogPubRec": {"monotonic_trend": "ascending"},
#     "NumTrades90Ever2DerogPubRec": {"monotonic_trend": "ascending"},
#     "PercentTradesNeverDelq": {"monotonic_trend": "descending"},
#     "MSinceMostRecentDelq": {"monotonic_trend": "descending"},
#     "NumTradesOpeninLast12M": {"monotonic_trend": "ascending"},
#     "MSinceMostRecentInqexcl7days": {"monotonic_trend": "descending"},
#     "NumInqLast6M": {"monotonic_trend": "ascending"},
#     "NumInqLast6Mexcl7days": {"monotonic_trend": "ascending"},
#     "NetFractionRevolvingBurden": {"monotonic_trend": "ascending"},
#     "NetFractionInstallBurden": {"monotonic_trend": "ascending"},
#     "NumBank2NatlTradesWHighUtilization": {"monotonic_trend": "ascending"},
# }

# def load_json(filename):
#     with open(file=filename, mode="r", encoding="utf-8") as file_header:
#         data = json.load(file_header)

#     return data


def _remove_feature(df: pd.DataFrame, columns_to_drop: str | list[str] | None = None):
    if columns_to_drop is None:
        return df
    if isinstance(columns_to_drop, str):
        columns_to_drop = [columns_to_drop]

    columns_to_drop = list(set(columns_to_drop).intersection(set(df.columns.values)))
    return df.drop(columns=columns_to_drop)


def remove_feature_with_low_variance(df):
    var_reductor = VarianceThreshold().set_output(transform="pandas")
    data_ = var_reductor.fit_transform(df)
    return data_


def load_data(path, drop_cols=None):
    df = pd.read_parquet(path)
    if drop_cols:
        columns_to_drop = list(set(drop_cols).intersection(set(df.columns.values)))
        return df.drop(columns=columns_to_drop)
    return df


def _get_binning_features(df, *, target=None, features=None):
    """
    Setup the binning process for optbinning.

    Args:
        binning_fit_params: fit parameters object, including splits
        features: the list of features that we are interested in
        target: the target variable
        df (DataFrame): Dataframe containing features and a target column called 'target'

    Returns: Optbinning functional to bin the data BinningProcess()

    """
    # Remove target if present in data
    if target:
        df = _remove_feature(df=df, columns_to_drop=target)

    binning_features = features or df.columns.to_list()
    categorical_features = (
        df[binning_features]
        .select_dtypes(include=["object", "category", "string"])
        .columns.values
    )

    return binning_features, categorical_features


def _stage_info(stage, symbol="=", length=100):
    msg = f"\n{symbol*length}\n{stage.center(length, symbol)}\n{symbol*length}"
    return msg

def set_destination_directory():
    root_dir = Path(DATA_DIR).joinpath(test_dir)
    predecessor_dir = None
    destination_dir = root_dir.joinpath(STAGE)
    destination_dir.mkdir(parents=True, exist_ok=True)
    logging.debug(f"Working dir is:  {destination_dir}")

    return predecessor_dir, destination_dir, root_dir

@timeit
def main(use_manual_bins=False, binning_fit_params=None):
    logging.info(_stage_info(STAGE))
    
    predecessor_dir, destination_dir, root_dir = set_destination_directory()
    # Get raw data and split into X and y
    if binning_fit_params is None:
        binning_fit_params = read_json(FILE_DIR/"configs/binning-params.json")

    x_train = pd.read_parquet(path=os.path.join(DATA_DIR, "X_train.parquet"))
    y_train = pd.read_parquet(path=os.path.join(DATA_DIR, "y_train.parquet"))

    logging.debug("Using automatic bins")
    X = remove_feature_with_low_variance(x_train)
    y = y_train.astype("int8").values.reshape(-1)

    binning_features, categorical_features = _get_binning_features(df=X)

    binning_process = BinningProcess(
        categorical_variables=categorical_features,
        variable_names=binning_features,
        # Uncomment the below line and pass a binning fit parameter
        # to stop doing automatic binning
        binning_fit_params=binning_fit_params,
        # This is the prebin size that should make the feature set usable
        min_prebin_size=10e-5,
        special_codes=SPECIAL_CODES,
    )
    binning_process.fit(X, y)

    preprocess_data = binning_process.transform(X, metric="woe")
    preprocess_data[TARGET] = y

    # save binning process and table
    save_artifacts(use_manual_bins=use_manual_bins, binning_process=binning_process, preprocess_data=preprocess_data, dest_dir=destination_dir)


    # logging.info(f"Time taken : {round(time.perf_counter() - start_time, 2)} seconds")


def save_artifacts(
    use_manual_bins: bool,
    binning_process: BinningProcess,
    preprocess_data: pd.DataFrame,
    dest_dir: Path
):
    iv_table_name = "manual_iv_table" if use_manual_bins else "auto_iv_table"
    iv_table = binning_process.summary()
    iv_table.to_csv(dest_dir.joinpath(f"{iv_table_name}.csv"))
    preprocess_data.to_parquet(dest_dir.joinpath(TRANSFORM_DATA_PATH))

    if SAVE_BINNING_OBJ:
        binning_process.save(str(dest_dir.joinpath(BINNING_TRANSFORM_PATH)))


if __name__ == "__main__":
    main()
