"""
Preprocessing of data.

This script performs the preprocessing of the data used to build the model.

python -m src.preprocess
"""
# import json
import logging
import os
# import time
import warnings
# from dataclasses import dataclass
from pathlib import Path

import hydra
import pandas as pd
from omegaconf import DictConfig, OmegaConf
from optbinning import BinningProcess
from sklearn.feature_selection import VarianceThreshold

# from src import config
from src.tools import (
    read_json,
    # save_dict_to_json,
    stage_info,
    timeit,
    )

# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(
    format='%(levelname)s:%(message)s', encoding='utf-8', level=logging.DEBUG
)

warnings.filterwarnings("ignore", category=DeprecationWarning)

# TARGET: str = "RiskPerformance"
SAVE_BINNING_OBJ = True
# BINNING_TRANSFORM_PATH = "binning-transformer.pkl"
# TRANSFORM_DATA_PATH = "transform-data.parquet"
# SPECIAL_CODES = [-9, -8, -7]
# MISSING = [-99_000_000]

# DATA_DIR = "data"
STAGE = "preprocessing"
# test_dir = 'dev-test'
# dest_dir = Path(DATA_DIR).joinpath(test_dir, STAGE)

FILE_DIR = Path(__file__).parent


def _remove_feature(frame: pd.DataFrame, columns_to_drop: str | list[str] | None = None):
    if columns_to_drop is None:
        return frame
    if isinstance(columns_to_drop, str):
        columns_to_drop = [columns_to_drop]

    columns_to_drop = list(set(columns_to_drop).intersection(set(frame.columns.values)))
    return frame.drop(columns=columns_to_drop)


def remove_feature_with_low_variance(frame: pd.DataFrame) -> pd.DataFrame:
    """Removes features with no variance.

    Use Variance to remove unused features.

    Args:
        frame (pd.DataFrame): Data to removed features with low variance.

    Returns:
        pd.DataFrame: Reduced data.
    """
    var_reductor = VarianceThreshold().set_output(transform="pandas")
    data_ = var_reductor.fit_transform(frame)
    return data_


def load_data(path: str | Path, drop_cols: list[str] | None = None) -> pd.DataFrame:
    """Loads data and return specific columns.

    Args:
        path (str): Path to data
        drop_cols (List, optional): List of columns. Defaults to None.

    Returns:
        pd.DataFrame: Read data as a Dataframe
    """
    frame = pd.read_parquet(path)
    if drop_cols:
        columns_to_drop = list(set(drop_cols).intersection(set(frame.columns.values)))
        return frame.drop(columns=columns_to_drop)
    return frame


def _get_binning_features(frame, *, target=None, features=None):
    """
    Setup the binning process for optbinning.

    Args:
        binning_fit_params: fit parameters object, including splits
        features: the list of features that we are interested in
        target: the target variable
        frame (DataFrame): Dataframe containing features and a target column called 'target'

    Returns: Optbinning functional to bin the data BinningProcess()

    """
    # Remove target if present in data
    if target:
        frame = _remove_feature(frame=frame, columns_to_drop=target)

    binning_features = features or frame.columns.to_list()
    categorical_features = (
        frame[binning_features]
        .select_dtypes(include=["object", "category", "string"])
        .columns.values
    )

    return binning_features, categorical_features


# def _stage_info(stage, symbol="=", length=100):
#     msg = f"\n{symbol*length}\n{stage.center(length, symbol)}\n{symbol*length}"
#     return msg


def set_destination_directory(cfg: DictConfig):
    """Prepares the directories.

    Args:
        cfg (DictConfig): Configuration data

    Returns:
        list[Path]: List of directories
    """
    root_dir = Path(cfg.data.source).joinpath(cfg.data.test_dir)
    predecessor_dir = None
    destination_dir = root_dir.joinpath(STAGE)
    destination_dir.mkdir(parents=True, exist_ok=True)
    logging.debug(f"Working dir is:  {destination_dir}") # pylint: disable=logging-fstring-interpolation

    return predecessor_dir, destination_dir, root_dir


def save_artifacts(
    use_manual_bins: bool,
    binning_process: BinningProcess,
    preprocess_data: pd.DataFrame,
    dest_dir: Path,
    cfg: DictConfig,
):
    """Save artifacts to specified directories.

    Args:
        use_manual_bins (bool): Type of bins to use
        binning_process (BinningProcess): Optbinning binning object
        preprocess_data (pd.DataFrame): Dataframe of transformed data
        dest_dir (Path): Directory to save data
        cfg (DictConfig): Configuration files
    """
    iv_table_name = "manual_iv_table" if use_manual_bins else "auto_iv_table"
    iv_table = binning_process.summary()
    iv_table.to_csv(dest_dir.joinpath(f"{iv_table_name}.csv"))
    preprocess_data.to_parquet(dest_dir.joinpath(cfg.preprocessing.transformed_data))

    if SAVE_BINNING_OBJ:
        binning_process.save(
            str(dest_dir.joinpath(cfg.preprocessing.binning_transformer))
        )


@timeit(logging.info)
@hydra.main(version_base=None, config_path="..", config_name="params")
def main(cfg: DictConfig, use_manual_bins=False, binning_fit_params=None):
    """Main function that runs all processes."""
    logging.info(stage_info(STAGE))
    OmegaConf.resolve(cfg)

    _, destination_dir, _ = set_destination_directory(cfg)
    # Get raw data and split into X and y
    if cfg.preprocessing.process == "manual":
        binning_fit_params = read_json(FILE_DIR / "configs/binning-params.json")

    x_train = pd.read_parquet(path=os.path.join(cfg.data.source, "X_train.parquet"))
    y_train = pd.read_parquet(path=os.path.join(cfg.data.source, "y_train.parquet"))

    logging.debug("Using automatic bins")
    x_reduced = remove_feature_with_low_variance(x_train)
    y_train = y_train.astype("int8").values.reshape(-1)

    binning_features, categorical_features = _get_binning_features(frame=x_reduced)

    binning_process = BinningProcess(
        categorical_variables=categorical_features,
        variable_names=binning_features,
        # Below params are manual
        binning_fit_params=binning_fit_params,
        min_prebin_size=cfg.preprocessing.min_prebin_size,
        special_codes=list(cfg.data.special_codes),
        selection_criteria={"iv": {"min": cfg.preprocessing.selection_strategy.iv.min}},
    )
    binning_process.fit(x_reduced, y_train)

    preprocessed_data = binning_process.transform(x_reduced, metric="woe")
    preprocessed_data[cfg.data.target] = y_train

    # save binning process and table
    save_artifacts(
        cfg=cfg,
        use_manual_bins=use_manual_bins,
        binning_process=binning_process,
        preprocess_data=preprocessed_data,
        dest_dir=destination_dir,
    )

    # logging.info(f"Time taken : {round(time.perf_counter() - start_time, 2)} seconds")


if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter
