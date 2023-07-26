import json
import logging as log
import os
import time
from pathlib import Path
from typing import Dict, Union

import hydra
import pandas as pd
from omegaconf import DictConfig
from sklearn.feature_selection import VarianceThreshold
from src.tools import stage_info
from varclushi import VarClusHi

DATA_DIR = "data"
PREV_STAGE = "preprocessing"
STAGE = "clustering"
test_dir = 'dev-test'

root_dir = Path(DATA_DIR).joinpath(test_dir)
predecessor_dir = root_dir.joinpath("preprocessing")
dest_dir = root_dir.joinpath(STAGE)


def remove_feature_with_low_variance(df):
    var_reductor = VarianceThreshold().set_output(transform="pandas")
    data_ = var_reductor.fit_transform(df)
    return data_


# log = Logger(stream_level="DEBUG", file_level="DEBUG").getLogger()
log.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=log.DEBUG)


class Cluster:
    def __init__(
        self,
        data: pd.DataFrame,
        iv_table: Union[pd.DataFrame, None] = None,
        max_eigen=1,
    ) -> None:
        # self.data = data
        self.iv_table = iv_table
        self.clusters = VarClusHi(data, maxeigval2=max_eigen, maxclus=None)

    def get_clusters(self):
        self.clusters.varclus()
        if self.iv_table is None:
            log.info("Retriving clusters without IVs")
            return self.clusters.rsquare

        log.info("Retriving clusters with IV for each feature")
        return pd.merge(
            self.clusters.rsquare,
            self.iv_table,
            how="left",
            left_on="Variable",
            right_on="name",
        )

    @staticmethod
    def get_best_feature_from_each_cluster(
        cluster_table: pd.DataFrame, feature: str = "Variable"
    ):
        # The best feature from each cluster is the one with the min RS Ratio
        # from that cluster. If the feature with the highest IV is different
        # than the one with the highest RS Ratio, it is included as well.
        if "iv" in cluster_table.columns:
            highest_iv = cluster_table.loc[
                cluster_table.groupby(["Cluster"])["iv"].idxmax()
            ][feature].tolist()
        else:
            highest_iv = []

        lowest_rs_ratio = cluster_table.loc[
            cluster_table.groupby(["Cluster"])["RS_Ratio"].idxmin()
        ][feature].tolist()

        return list(set(highest_iv + lowest_rs_ratio))

    @classmethod
    def read_iv_table(cls, path: str, cutoff: float = 0.0):
        # Read IV table from path and filter based on cutoff
        return pd.read_csv(path).query(f"iv >= {cutoff}")

    @classmethod
    def save(cls, data: Dict, path):
        with open(path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=6)


# TODO: Move this function to a centralized location
def load_transformed_data(path, keep_columns=None, **kwargs):
    # Load transformed data and return only cols with non singular value
    # Opportunity to check type
    # Things to check includes:
    # 1. All columns are numerical
    # 2. All columns have some variance
    data = pd.read_parquet(path, **kwargs)
    if keep_columns:
        data = data[keep_columns]
    data = remove_feature_with_low_variance(data)
    return data


# FIXME: Remove this if not needed
def load_json(filename):
    with open(file=filename, mode="r", encoding="utf-8") as file_header:
        data = json.load(file_header)

    return data


# TODO: Add data classes that ensure params in cfg are pasrsed as specidied
@hydra.main(version_base=None, config_path="..", config_name="params")
def main(cfg: DictConfig):
    log.info(stage_info(stage=STAGE))
    start_time = time.perf_counter()
    # Define storage for data
    os.makedirs(path := dest_dir, exist_ok=True)
    log.info(f"Working dir is:  {path=}")
    
    iv_table_name = _compose_iv_table_name(cfg.preprocessing.auto_bins)
    iv_table = Cluster.read_iv_table(
        path=predecessor_dir.joinpath(iv_table_name), 
        cutoff=cfg.iv_criteria.min,
    )
    transformed_data = load_transformed_data(
        path=predecessor_dir.joinpath("transform-data.parquet"),
        keep_columns=iv_table.name.to_list(),
    )

    # Clustering
    clusters = Cluster(
        data=transformed_data, iv_table=iv_table, max_eigen=cfg.cluster.max_eigen_split
    )
    # Get rsquare and IV table and save
    r_square_iv_table = clusters.get_clusters()
    # Selected features by variable clustering
    selected_features_varclushi = clusters.get_best_feature_from_each_cluster(
        cluster_table=r_square_iv_table, 
        feature="Variable",
    )
    
    save_artifacts(path, r_square_iv_table, selected_features_varclushi)


    log.info(stage_info(
        stage=f"Time taken: {round(time.perf_counter() - start_time, 2)} seconds"
        ))

def _compose_iv_table_name(auto_bins):
    if auto_bins is True:
        return "auto_iv_table.csv"
    return "manual_iv_table.csv"

def save_artifacts(path, r_square_iv_table, selected_features_varclushi):
    if "iv" in r_square_iv_table.columns:
        r_square_iv_table.to_csv(os.path.join(path, "r_square_iv_table.csv"))
    else:
        r_square_iv_table.to_csv(os.path.join(path, "r_square_table.csv"))

    Cluster.save(
        data={"selected-features-varclushi": selected_features_varclushi},
        path=os.path.join(path, "selected-features-varclushi.json"),
    )

if __name__ == "__main__":
    main(None)
