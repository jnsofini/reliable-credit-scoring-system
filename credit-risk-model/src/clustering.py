""" 
Run from the credit-risk-model directory, with pipenv from reliable-credit-scoring-system
python -m src.clustering 
"""
import json
import logging as log
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union

import hydra
import pandas as pd
from omegaconf import DictConfig
from sklearn.feature_selection import VarianceThreshold
from src.ClusterClass import Cluster
from src.tools import read_json, save_dict_to_json, stage_info, timeit
from varclushi import VarClusHi

TARGET: str = "RiskPerformance"

# DATA_DIR = "data"
STAGE = "clustering"
# test_dir = 'dev-test'

FILE_DIR = Path(__file__).parent


def set_destination_directory(cfg:DictConfig):
    root_dir = Path(cfg.data.source).joinpath(cfg.data.test_dir)
    predecessor_dir = root_dir.joinpath("preprocessing")
    destination_dir = root_dir.joinpath(STAGE)
    destination_dir.mkdir(parents=True, exist_ok=True)
    log.debug(f"Working dir is:  {destination_dir}")

    return predecessor_dir, destination_dir, root_dir


def log_feature_summary(features_in: int | list, features_out: list[str]):
    """Log summary of the features in and out of the stage.

    Args:
        features_in (int): number of features in
        features_out (list[str]): number of features out of the stage
    """

    log.info(f"The number of features to select from is: {features_in}")
    log.info(f"The number of features selected is: {len(features_out)}")
    log.info("The number of features selected: ")
    log.info(features_out)


def remove_feature_with_low_variance(df):
    var_reductor = VarianceThreshold().set_output(transform="pandas")
    data_ = var_reductor.fit_transform(df)
    return data_


def _compose_iv_table_name(auto_bins):
    if auto_bins is True:
        return "auto_iv_table.csv"
    return "manual_iv_table.csv"


def save_artifacts(path, cluster_iv_table, selected_features_varclushi):
    if "iv" in cluster_iv_table.columns:
        cluster_iv_table.to_csv(os.path.join(path, "cluster_iv_table.csv"))
    else:
        cluster_iv_table.to_csv(os.path.join(path, "cluster_table.csv"))

    Cluster.save(
        data={"selected-features-varclushi": selected_features_varclushi},
        path=os.path.join(path, "selected-features-varclushi.json"),
    )


# log = Logger(stream_level="DEBUG", file_level="DEBUG").getLogger()
log.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=log.DEBUG)


# TODO: Add data classes that ensure params in cfg are pasrsed as specidied
@timeit(log.info)
@hydra.main(version_base=None, config_path="..", config_name="params")
def main(cfg: DictConfig):
    log.info(stage_info(stage=STAGE))
    # start_time = time.perf_counter()
    # Define storage for data
    predecessor_dir, destination_dir, root_dir = set_destination_directory(cfg)

    log.info(f"Working dir is:  {destination_dir}")

    iv_table_name = _compose_iv_table_name(cfg.preprocessing.auto_bins)
    iv_table = Cluster.read_iv_table(
        path=predecessor_dir.joinpath(iv_table_name),
        cutoff=cfg.iv_criteria.min,
    )
    transformed_data = pd.read_parquet(
        path=predecessor_dir.joinpath("transform-data.parquet")
    )
    transformed_data.drop(columns=cfg.data.target, inplace=True)

    # Clustering
    clusters = Cluster(max_eigen=cfg.cluster.max_eigen_split)
    _ = clusters.fit_transform(X=transformed_data)

    # Get rsquare and IV table and save
    cluster_iv_table = clusters.get_clusters()
    # Selected features by variable clustering
    selected_features_varclushi = clusters.get_best_feature_from_each_cluster(
        cluster_table=cluster_iv_table,
        feature="Variable",
    )

    save_artifacts(destination_dir, cluster_iv_table, selected_features_varclushi)


if __name__ == "__main__":
    main(None)
