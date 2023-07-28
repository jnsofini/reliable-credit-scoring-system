""" 
Run from the credit-risk-model directory, with pipenv from reliable-credit-scoring-system
python -m src.scorecard 
"""


import json
import os
import time
from pathlib import Path
from dataclasses import dataclass
import logging as log

import mlflow
import pandas as pd
from optbinning import BinningProcess, Scorecard
from optbinning.scorecard import plot_auc_roc, plot_cap, plot_ks
from sklearn.linear_model import LogisticRegression  # , LogisticRegressionCV
from src.util import scorecard, setup_binning, _get_binning_features, _get_categorical_features  # ,load_data
from src.tools import stage_info, read_json, save_dict_to_json, timeit
from src.metrics import formatted_metrics, get_population_dist
# # Set MLFLOW
# db = (
#     "/home/fini/github-projects/reliable-credit-scoring-system/"
#     "data/experiment-tracking/mlflow.db"
# )


# mlflow.set_tracking_uri(f"sqlite:///{db}")
# mlflow.set_experiment("scorecard-experiment")

TARGET: str = "RiskPerformance"
SPECIAL_CODES = [-9, -8, -7]
MISSING = [-99_000_000]

DATA_DIR = "data"
STAGE = "train"
test_dir = 'dev-test'
# root_dir = Path(DATA_DIR).joinpath(test_dir)
# predecessor_dir = root_dir.joinpath("featurization")
# dest_dir = root_dir.joinpath(STAGE)

FILE_DIR = Path(__file__).parent

MAX_ITER_LOGREG: int = 1000

FEATURE_SELECTION_TYPE: str = "rfecv"

# log = Logger(stream_level="DEBUG", file_level="DEBUG").getLogger()
log.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=log.DEBUG)

def set_destination_directory():
    root_dir = Path(DATA_DIR).joinpath(test_dir)
    predecessor_dir = root_dir.joinpath("featurization")
    destination_dir = root_dir.joinpath(STAGE)
    destination_dir.mkdir(parents=True, exist_ok=True)
    log.debug(f"Working dir is:  {destination_dir}")

    return predecessor_dir, destination_dir, root_dir

def save_metrics_to_output(y, y_pred, base_path):
    os.makedirs(os.path.join(base_path), exist_ok=True)
    plot_auc_roc(y, y_pred, savefig=False, fname=f"{base_path}/auc.png")
    plot_cap(y, y_pred, savefig=False, fname=f"{base_path}/cap.png")
    plot_ks(y, y_pred, savefig=False, fname=f"{base_path}/ks.png")

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

def scorecard_pipeline(data, selected_features, target=TARGET, binning_fit_params=None):
    binning_process = setup_binning(
        data[selected_features],
        target=target,
        features=selected_features,
        binning_fit_params=binning_fit_params,
    )

    # method = LogisticRegressionCV(
    #     Cs=3,
    #     cv=5,
    #     penalty="l1",
    #     scoring="roc_auc",
    #     solver="liblinear",
    #     max_iter=MAX_ITER_LOGREG,
    #     random_state=42,
    # )
    method = LogisticRegression(C=3, max_iter=MAX_ITER_LOGREG, random_state=42)

    scorecard_ = scorecard(binning_process, method=method)

    X = data[selected_features]
    y = data[target].astype("int8")

    return scorecard_.fit(X, y)


@timeit(log.info)
def main(
    feature_selector=FEATURE_SELECTION_TYPE,
    binning_fit_params=None
    # use_manual_bins=True,
):
    log.debug(stage_info(stage=STAGE))

    predecessor_dir, destination_dir, root_dir = set_destination_directory()
    log.debug(f"Working dir is:  {destination_dir}")

    ft = read_json(path=predecessor_dir.joinpath(f"selected-features-{feature_selector}.json"))
    scorecard_features = ft[f"selected-features-{feature_selector}"]
    log.info("Using automatic bins")
    if binning_fit_params is None:
        binning_fit_params = read_json(FILE_DIR / "configs/binning-params.json")

    X_train = pd.read_parquet(
        os.path.join(DATA_DIR, "X_train.parquet")
    )
    X_train = X_train[scorecard_features]
    y_train = pd.read_parquet(
        os.path.join(DATA_DIR, "y_train.parquet")
    )
    y_train = y_train.values.reshape(-1).astype("int8")

    categorical_features = _get_categorical_features(X_train)
    binning_process = BinningProcess(
        categorical_variables=categorical_features,
        variable_names=list(X_train.columns),
        binning_fit_params={key: value for key, value in binning_fit_params.items() if key in scorecard_features},
        min_prebin_size=10e-5,
        special_codes=SPECIAL_CODES,
    )

    estimator = LogisticRegression(C=3, max_iter=MAX_ITER_LOGREG, random_state=42)
    scorecard_model = get_scorecard_obj(
        process=binning_process,
        method=estimator
    )
    scorecard_model.fit(X_train, y_train)

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
    print(table.groupby("Variable")["IV"].sum().sort_values(ascending=True))
    table.to_csv(destination_dir.joinpath(f"model-{feature_selector}.csv"))

    

    # # do prediction
    y_pred = scorecard_model.predict_proba(X_train[scorecard_features])[:, 1]
    auc_gini_ks = formatted_metrics(y=y_train, y_pred=y_pred)
    dist_stats = get_population_dist(y=y_train)
    print({
            "metrics": auc_gini_ks,
            "dist": dist_stats
        })
    save_dict_to_json(
        filename=destination_dir.joinpath(f"summary-stats-{feature_selector}.json"), 
        default=str,
        data={
            "metrics": auc_gini_ks,
            "dist": dist_stats
        })
    # save_metrics_to_output(
    #     y=y_train,
    #     y_pred=y_pred,
    #     base_path=str(destination_dir)
    # )


if __name__ == "__main__":
    main()
