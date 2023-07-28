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
from optbinning.scorecard import plot_auc_roc, plot_cap, plot_ks
from sklearn.linear_model import LogisticRegression  # , LogisticRegressionCV
from src.util import scorecard, setup_binning  # ,load_data
from src.tools import stage_info, read_json, save_dict_to_json, timeit

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

# log = Logger(stream_level="DEBUG", file_level="DEBUG").getLogger()
log.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=log.DEBUG)

def set_destination_directory():
    root_dir = Path(DATA_DIR).joinpath(test_dir)
    predecessor_dir = root_dir.joinpath("featurization")
    destination_dir = root_dir.joinpath(STAGE)
    destination_dir.mkdir(parents=True, exist_ok=True)
    log.debug(f"Working dir is:  {destination_dir}")

    return predecessor_dir, destination_dir, root_dir

def save_metrics_to_output(y, y_pred, path):
    base_path = path
    os.makedirs(os.path.join(base_path), exist_ok=True)
    plot_auc_roc(y, y_pred, savefig=True, fname=f"{base_path}/auc.png")
    plot_cap(y, y_pred, savefig=True, fname=f"{base_path}/cap.png")
    plot_ks(y, y_pred, savefig=True, fname=f"{base_path}/ks.png")


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
    # use_manual_bins=True,
):
    log.debug(stage_info(stage=STAGE))

    predecessor_dir, destination_dir, root_dir = set_destination_directory()
    log.debug(f"Working dir is:  {destination_dir}")

    X_train = pd.read_parquet(
        os.path.join(DATA_DIR, "X_train.parquet")
    )
    y_train = pd.read_parquet(
        os.path.join(DATA_DIR, "y_train.parquet")
    )

    # Pull all data back together as the functions were written to take that
    train_data = X_train
    train_data[TARGET] = y_train

    with open(
        file=predecessor_dir.joinpath(f"selected-features-{feature_selector}.json"),
        mode="r",
        encoding="utf-8",
    ) as fh:
        ft = json.load(fh)
    scorecard_features = ft[f"selected-features-{feature_selector}"]

    print("Using automatic bins")
    binning_fit_params = BINNING_FIT_PARAMS
    # X = X_train[
    # [col for col in X_train.columns if X_train[col].nunique()>1]
    # ]#.drop(columns=["SNAPSHOT_DT", "B1_BUS_PRTNR_NBR"])
    # y = y_train.astype("int8").values.reshape(-1)

    # scorecard_features = [
    #     col for col in selection_step_features if X_train[col].nunique() > 1
    # ]
    # if include_financials:
    #     scorecard_features = scorecard_features + dlfeatures.financial_features

    # print("Features used to build the model are: \n", scorecard_features)
    # enable autologging

    scorecard_model = scorecard_pipeline(
        data=train_data[scorecard_features + [TARGET]],
        selected_features=scorecard_features,
        target=TARGET,
        binning_fit_params=binning_fit_params,
    )
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

    # do prediction
    y_pred = scorecard_model.predict_proba(train_data[scorecard_features])[:, 1]
    save_metrics_to_output(
        y=train_data[TARGET].astype("int8"),
        y_pred=y_pred,
        path=str(destination_dir),
    )


if __name__ == "__main__":
    main()
