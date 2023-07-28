import json
import logging as log
from pathlib import Path

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from varclushi import VarClusHi


class Cluster(BaseEstimator, TransformerMixin):
    """
    Clustering Transformer for Feature Selection.

    This transformer clusters features based on their similarity and selects one feature from each cluster
    based on the lowest RS Ratio. If available, the feature with the highest IV is also included.
    It uses VarClusHi for clustering, a library that functions similarly to the SAS version.
    """

    def __init__(self, max_eigen=1, maxclus=None) -> None:
        """
        Initialize the Cluster transformer.

        Parameters:
            max_eigen (int, optional): Maximum number of eigenvalues for clustering. Defaults to 1.
            maxclus (int, optional): Maximum number of clusters to generate. Defaults to None.
        """
        self.max_eigen = max_eigen
        self.maxclus = maxclus

    def fit(self, x, y=None):
        """
        Fit the Cluster transformer to the data.

        Parameters:
            x (pd.DataFrame): Input data.
            y: Ignored.

        Returns:
            self: Fitted Cluster transformer object.
        """
        self.clusters = VarClusHi(df=x, maxeigval2=self.max_eigen, maxclus=self.maxclus)
        return self

    def transform(self, x):
        """
        Transform the input data based on feature selection.

        Parameters:
            x (pd.DataFrame): Input data.

        Returns:
            pd.DataFrame: Transformed data with selected features.
        """
        file = Path("data/pipeline/auto-iv-table.csv")
        if file.is_file():
            iv_table = self.read_iv_table(file).round(2)
        else:
            iv_table = None
        self.cluster_table = self.get_clusters(iv_table)
        self.selected_features = self.get_best_feature_from_each_cluster(
            cluster_table=self.cluster_table, feature="Variable"
        )
        cluster_table = self._indicated_selected(
            self.cluster_table, self.selected_features
        )
        Path("data/pipeline").mkdir(parents=True, exist_ok=True)
        cluster_table.to_csv("data/pipeline/cluster-iv-table.csv")
        return x[self.selected_features]

    @staticmethod
    def _indicated_selected(table, selected, features="Variable"):
        """
        Mark selected features in the cluster table.

        Parameters:
            table (pd.DataFrame): Cluster table.
            selected (list): List of selected features.
            features (str, optional): Name of the feature column. Defaults to "Variable".

        Returns:
            pd.DataFrame: Cluster table with marked selected features.
        """
        return table.assign(cluster_iv_selection=table[features].isin(selected))

    def get_clusters(self, iv_table=None):
        """
        Retrieve clusters with or without IV for each feature.

        Parameters:
            iv_table (pd.DataFrame, optional): IV table. Defaults to None.

        Returns:
            pd.DataFrame: Cluster table with or without IV.
        """
        self.clusters.varclus()
        self.iv_table = iv_table
        if self.iv_table is None:
            log.info("Retrieving clusters without IVs")
            return self.clusters.rsquare

        log.info("Retrieving clusters with IV for each feature")
        return pd.merge(
            self.clusters.rsquare.round(2),
            self.iv_table,
            how="left",
            left_on="Variable",
            right_on="name",
        )

    @staticmethod
    def get_best_feature_from_each_cluster(
        cluster_table: pd.DataFrame, feature: str = "Variable"
    ):
        """
        Get the best feature from each cluster.

        Parameters:
            cluster_table (pd.DataFrame): Cluster table with RS Ratio and IV.
            feature (str, optional): Name of the feature column. Defaults to "Variable".

        Returns:
            list: List of selected features.
        """
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
    def read_iv_table(cls, path: Path | str, cutoff: float = 0.0):
        """
        Read IV table from a given path and filter based on a cutoff.

        Parameters:
            path (Path or str): Path to the IV table CSV file.
            cutoff (float, optional): IV cutoff value. Defaults to 0.0.

        Returns:
            pd.DataFrame: IV table after filtering.
        """
        return pd.read_csv(path).query(f"iv >= {cutoff}")

    @classmethod
    def save(cls, data: dict, path):
        """
        Save data to a given file path.

        Parameters:
            data (dict): Data to be saved.
            path (str): File path for saving the data.
        """
        with open(path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=6)
