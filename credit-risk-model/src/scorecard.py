""" 
Run from the credit-risk-model directory, with pipenv from reliable-credit-scoring-system
python -m src.scorecard 
"""
# pylint: disable=logging-fstring-interpolation

import json
import logging as log
import os

# import time
# from dataclasses import dataclass
from pathlib import Path

import hydra

# import mlflow
import pandas as pd
from omegaconf import DictConfig
from optbinning import BinningProcess, Scorecard
from optbinning.scorecard import plot_auc_roc, plot_cap, plot_ks
from sklearn.linear_model import LogisticRegression  # , LogisticRegressionCV
from src.metrics import formatted_metrics, get_population_dist
from src.tools import read_json, save_dict_to_json, stage_info, timeit
from src.util import (  # ,load_data
    # _get_binning_features,
    _get_categorical_features,
)

# # Set MLFLOW
# db = (
#     "/home/fini/github-projects/reliable-credit-scoring-system/"
#     "data/experiment-tracking/mlflow.db"
# )


# mlflow.set_tracking_uri(f"sqlite:///{db}")
# mlflow.set_experiment("scorecard-experiment")

# TARGET: str = "RiskPerformance"
# SPECIAL_CODES = [-9, -8, -7]
# MISSING = [-99_000_000]

# DATA_DIR = "data"
STAGE = "train"
# test_dir = 'dev-test'
# root_dir = Path(DATA_DIR).joinpath(test_dir)
# predecessor_dir = root_dir.joinpath("featurization")
# dest_dir = root_dir.joinpath(STAGE)

FILE_DIR = Path(__file__).parent

# MAX_ITER_LOGREG: int = 1000

# FEATURE_SELECTION_TYPE: str = "rfecv"

# log = Logger(stream_level="DEBUG", file_level="DEBUG").getLogger()
log.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=log.DEBUG)


def set_destination_directory(cfg: DictConfig):
    """Prepares the directories.

    Args:
        cfg (DictConfig): Configuration data

    Returns:
        list[Path]: List of directories
    """
    root_dir = Path(cfg.data.source).joinpath(cfg.data.test_dir)
    predecessor_dir = root_dir.joinpath("featurization")
    destination_dir = root_dir.joinpath(STAGE)
    destination_dir.mkdir(parents=True, exist_ok=True)
    log.debug(f"Working dir is:  {destination_dir}")

    return predecessor_dir, destination_dir, root_dir


def save_metrics_to_output(y_true, y_pred, base_path):
    """Calculate artifacts from predict and save them."""
    Path(base_path).mkdir(parents=True, exist_ok=True)
    plot_auc_roc(y_true, y_pred, savefig=False, fname=f"{base_path}/auc.png")
    plot_cap(y_true, y_pred, savefig=False, fname=f"{base_path}/cap.png")
    plot_ks(y_true, y_pred, savefig=False, fname=f"{base_path}/ks.png")


def get_scorecard_obj(process, *, method=None):
    """
    Model estimator to be used for fitting.

    Args:
        process: Optbinning binning process operator
        method: Scikit learn estimator for fitting

    Returns:
        A Scorecard object
    """
    if method is None:
        method = LogisticRegression()

    scaling_method: str = "pdo_odds"
    # scaling_method_data = {
    #     "min": 350,
    #     "max": 850,
    # }
    scaling_method_data = {"pdo": 30, "odds": 20, "scorecard_points": 750}
    return Scorecard(
        binning_process=process,
        estimator=method,
        scaling_method=scaling_method,
        scaling_method_params=scaling_method_data,
        intercept_based=True,
        reverse_scorecard=False,
        rounding=True
        # scaling_method="pdo_odds",
        # scaling_method_params={
        #     "pdo": 30,
        #     # "odd":1,
        #     # "scorecard_points": 30
        # }
    )


def get_binning_params(binning_type: str, selected_features: list):
    """Loads binning features are filter only those selected by feature selection.

    Args:
        binning_type (str): Type of binning.
        selected_features (list[str]): List of features from previous process stage
    """

    if binning_type == "manual":
        binning_fit_params = read_json(FILE_DIR / "configs/binning-params.json")
        log.info("Using manual bins")
    else:
        binning_fit_params = {}
        log.info("Using automatic bins")

    return {
        key: value
        for key, value in binning_fit_params.items()
        if key in selected_features
    }


@timeit(log.info)
@hydra.main(version_base=None, config_path="..", config_name="params")
def main(
    cfg: DictConfig,
    feature_selector="rfecv"
    # use_manual_bins=True,
):
    """Main function that runs all processes."""
    log.debug(stage_info(stage=STAGE))

    predecessor_dir, destination_dir, _ = set_destination_directory(cfg=cfg)
    # log.debug(f"Working dir is:  {destination_dir}")

    feature_selection_file = read_json(
        path=predecessor_dir.joinpath(f"selected-features-{feature_selector}.json")
    )
    scorecard_features = feature_selection_file[f"selected-features-{feature_selector}"]
    binning_fit_params = get_binning_params(
        binning_type=cfg.scorecard.estimator.process,
        selected_features=scorecard_features,
    )

    x_train = pd.read_parquet(os.path.join(cfg.data.source, "X_train.parquet"))
    x_train = x_train[scorecard_features]
    y_train = pd.read_parquet(os.path.join(cfg.data.source, "y_train.parquet"))
    y_train = y_train.values.reshape(-1).astype("int8")

    # categorical_features = _get_categorical_features(x_train)
    binning_process = BinningProcess(
        categorical_variables=_get_categorical_features(x_train),
        variable_names=list(x_train.columns),
        binning_fit_params=binning_fit_params,
        min_prebin_size=cfg.preprocessing.min_prebin_size,
        special_codes=list(cfg.data.special_codes),
    )

    scorecard_model = get_scorecard_obj(
        process=binning_process,
        method=LogisticRegression(
            C=3,
            max_iter=cfg.scorecard.estimator.max_iter,
            random_state=cfg.pipeline.seed,
        ),
    )
    scorecard_model.fit(x_train, y_train)

    # with mlflow.start_run(run_name="Optbinning Model"):
    #     # mlflow.sklearn.save_model(
    #     #     path="model",
    #     #     sk_model=scorecard_model,
    #     #     serialization_format="pickle",
    #     #     )
    #     mlflow.sklearn.log_model(
    #         artifact_path="data/mlflow_artifacts_store",
    #         sk_model=scorecard_model,
    #         serialization_format="pickle",
    #         )
    # Save scorecard obj
    scorecard_model.save(str(destination_dir.joinpath(f"model-{feature_selector}.pkl")))

    table = scorecard_model.table(style="detailed").round(3)
    log.debug(table.groupby("Variable")["IV"].sum().sort_values(ascending=True))
    table.to_csv(destination_dir.joinpath(f"model-{feature_selector}.csv"))

    # # do prediction
    y_pred = scorecard_model.predict_proba(x_train[scorecard_features])[:, 1]
    auc_gini_ks = formatted_metrics(y_true=y_train, y_pred=y_pred)
    dist_stats = get_population_dist(y_true=y_train)
    log.info(json.dumps({"metrics": auc_gini_ks, "dist": dist_stats}, indent=6))
    save_dict_to_json(
        filename=destination_dir.joinpath(f"summary-stats-{feature_selector}.json"),
        default=str,
        data={"metrics": auc_gini_ks, "dist": dist_stats},
    )
    # save_metrics_to_output(
    #     y=y_train,
    #     y_pred=y_pred,
    #     base_path=str(destination_dir)
    # )


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
