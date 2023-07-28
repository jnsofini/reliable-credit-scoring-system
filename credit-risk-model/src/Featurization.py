""" 
Run from the credit-risk-model directory, with pipenv from reliable-credit-scoring-system
python -m src.Featurization 
"""

import json
import os
import warnings
import logging as log

import pandas as pd
from sklearn.feature_selection import RFECV, SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression
from typing import Literal
from pathlib import Path

from src.tools import stage_info, read_json, save_dict_to_json

from dataclasses import dataclass

warnings.filterwarnings("ignore", category=DeprecationWarning)


TARGET: str = "RiskPerformance"
TOP_FEATURE_NUM: int = 15
MAX_ITER_LOGREG: int = 1000
FEATURE_SELECTION_TYPE: str = "rfecv"

DATA_DIR = "data"
STAGE = "featurization"
test_dir = 'dev-test'

# root_dir = Path(DATA_DIR).joinpath(test_dir)
# predecessor_dir = root_dir.joinpath("clustering")
# dest_dir = root_dir.joinpath(STAGE)

FILE_DIR = Path(__file__).parent

log.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=log.DEBUG)


@dataclass
class FeatureSelectionParameters:
    selector: Literal["forward", "backward", "rfecv"] = "rfecv"
    num_feat_to_select: str | int = "auto"
    n_jobs: int = -1
    scoring: str = "roc_auc"

    def __post_init__(self):
        tol: float = 1e-3
        if self.selector == "forward":
            self.tol = tol
        elif self.selector == "backward":
            self.tol = -1 * tol


@dataclass
class SequentialFeatureParameters:
    direction: Literal["forward", "backward"] = "forward"
    n_features_to_select: str | int = "auto"
    n_jobs: int = -1
    scoring: str = "roc_auc"
    tol: float = 1e-3
    cv: int | None = None

    def __post_init__(self):
        if self.direction == "backward":
            self.tol = -1 * self.tol


class RFECVParameters:
    min_features_to_select: int = 5
    n_jobs: int = -1
    scoring: str = "roc_auc"
    cv: int | None = None


def _check_feature_selector(feature_selector):
    if feature_selector in ["forward", "backward", "rfecv"]:
        print(f"Feature selection process: {feature_selector}")
    else:
        NotImplemented(f"NOT Implemented Feature selection process: {feature_selector}")


def set_sequential_feature_selector(
    estimator, params: SequentialFeatureParameters
) -> SequentialFeatureSelector:
    return SequentialFeatureSelector(
        estimator=estimator,
        n_features_to_select=params.n_features_to_select,
        direction=params.direction,
        scoring=params.scoring,
        tol=params.tol,
        cv=params.cv,
        n_jobs=params.n_jobs,
    )


def set_rfecv_feature_selector(estimator, params: RFECVParameters) -> RFECV:
    return RFECV(
        estimator=estimator, scoring=params.scoring, cv=params.cv, n_jobs=params.n_jobs
    )


def set_feature_selection(
    estimator, params: SequentialFeatureParameters | RFECVParameters
):
    direction = getattr(params, "direction", "rfecv")
    _check_feature_selector(direction)

    if direction == "rfecv":
        feature_selector = set_rfecv_feature_selector(
            estimator=estimator, params=params
        )
    else:
        feature_selector = set_sequential_feature_selector(
            estimator=estimator, params=params
        )

    return feature_selector


def set_destination_directory():
    root_dir = Path(DATA_DIR).joinpath(test_dir)
    predecessor_dir = root_dir.joinpath("clustering")
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


def main(feature_selector=FEATURE_SELECTION_TYPE):
    log.debug(stage_info(stage=STAGE))

    # dest_dir.mkdir(parents=True, exist_ok=True)
    # log.debug(f"Working dir is:  {dest_dir}")
    predecessor_dir, destination_dir, root_dir = set_destination_directory()
    # breakpoint()
    transformed_data = pd.read_parquet(
        root_dir.joinpath("preprocessing", "transform-data.parquet")
    )

    log.info("Using automatic bins")
    ft = read_json(f"{predecessor_dir}/selected-features-varclushi.json")
    features_ = ft["selected-features-varclushi"]

    logreg = LogisticRegression(max_iter=MAX_ITER_LOGREG)
    pipeline_params = RFECVParameters()

    feat_selection_pipeline = set_feature_selection(
        estimator=logreg, params=pipeline_params
    )
    feat_selection_pipeline.fit(
        X=transformed_data[features_], y=transformed_data[TARGET].astype("int8")
    )

    log_feature_summary(
        features_in=len(features_),
        features_out=list(feat_selection_pipeline.get_feature_names_out()),
    )

    # save_dict_to_json(
    #     data={f"selected-features-{feature_selector}": selected_features_pl},
    #     filename=f"{dest_dir}/selected-features-{feature_selector}.json"
    #     )

    # with open(
    #     file=f"{destination_dir}/selected-features-{feature_selector}.json",
    #     mode="w",
    #     encoding="utf-8",
    # ) as f:
    #     json.dump(
    #         {f"selected-features-{feature_selector}": selected_features_pl}, f, indent=6
    #     )


if __name__ == "__main__":
    main()
