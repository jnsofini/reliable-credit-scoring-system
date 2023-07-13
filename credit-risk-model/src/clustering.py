"""
Module for feature clustering.
"""

import json
import os
import time

import pandas as pd

import config

from util import (
    filter_iv_table,
    get_best_feature_from_each_cluster,
    get_iv_from_binning_obj,
)
from varclushi import VarClusHi

MAX_EIGEN_SPLIT = 0.7
# SEGMENTATION = None #"alnc-vs-non-alnc"


def load_transformed_data(path):
    # Load transformed data and return only cols with non singular value
    transformed_data = pd.read_parquet(path)
    select_columns = transformed_data.columns[transformed_data.nunique() != 1]
    removed_columns = transformed_data.columns[transformed_data.nunique() == 1]
    print("The following columns are removed", removed_columns)
    return transformed_data[select_columns]


def main():
    print("===========================================================")
    print("==================Clustering===============================")
    print("===========================================================")
    start_time = time.perf_counter()
    os.makedirs(path := config.BASE_PATH, exist_ok=True)

    print(f"Artifacts directory is:  {path}")

    iv_table = get_iv_from_binning_obj(
        os.path.join(path, config.BINNING_TRANSFORM_PATH)
    )
    transformed_data_all = load_transformed_data(
        os.path.join(path, config.TRANSFORM_DATA_PATH)
    )

    modelling_features = list(
        set(
            filter_iv_table(iv_table, iv_cutoff=0.1, min_n_bins=2)
        )  # .intersection(params.model_features)
    )

    transformed_data = transformed_data_all[modelling_features]

    print(
        [
            col
            for col in transformed_data.columns
            if transformed_data[col].nunique() == 1
        ]
    )

    # model_data = raw_data[transformed_data.columns]

    # Using the transform data to get features and clusters

    clusters = VarClusHi(transformed_data, maxeigval2=MAX_EIGEN_SPLIT, maxclus=None)
    clusters.varclus()

    # Select best feature from each cluster
    r_square_iv_table = pd.merge(
        clusters.rsquare,
        iv_table[iv_table.name.isin(modelling_features)],
        how="left",
        left_on="Variable",
        right_on="name",
    ).round(3)

    r_square_iv_table.to_csv(os.path.join(path, "r_square_iv_table.csv"))
    # breakpoint()

    # Selected features by variable clustering
    selected_features = get_best_feature_from_each_cluster(r_square_iv_table)
    with open(
        file=os.path.join(path, "selected-features-varclushi.json"),
        mode="w",
        encoding="uff-8",
    ) as f:
        json.dump({"selected-features-varclushi": selected_features}, f, indent=6)

    print(f"Time taken : {round(time.perf_counter() - start_time, 2)} seconds")


if __name__ == "__main__":
    main()
