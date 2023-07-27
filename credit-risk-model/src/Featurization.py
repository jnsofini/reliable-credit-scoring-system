import json
import os
import warnings

import pandas as pd
from sklearn.feature_selection import RFECV, SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression
from typing import Literal
from pathlib import Path

from dataclasses import dataclass

warnings.filterwarnings("ignore", category=DeprecationWarning)


TARGET: str = "RiskPerformance"
TOP_FEATURE_NUM: int = 15
MAX_ITER_LOGREG: int = 1000
FEATURE_SELECTION_TYPE: str = "rfecv"

DATA_DIR = "data"
STAGE = "featurization"
test_dir = 'dev-test'

root_dir = Path(DATA_DIR).joinpath(test_dir)
predecessor_dir = root_dir.joinpath("clustering")
dest_dir = root_dir.joinpath(STAGE)

FILE_DIR = Path(__file__).parent


@dataclass
class FeatureSelectionParameters:
    selector: Literal["forward", "backward", "rfecv"] = "rfecv"
    num_feat_to_select: str | int = "auto"
    n_jobs: int = -1
    scoring: str ="roc_auc"

    def __post_init__(self):
        tol: float = 1e-3
        if self.selector == "forward":
            self.tol = tol
        elif self.selector == "backward":
            self.tol = -1*tol

@dataclass
class SequentialFeatureParameters:
    direction: Literal["forward", "backward"] = "forward"
    n_features_to_select: str | int = "auto"
    n_jobs: int = -1
    scoring: str ="roc_auc"
    tol: float = 1e-3
    cv: int | None  = None

    def __post_init__(self):
        if self.direction == "backward":
            self.tol = -1*self.tol

class RFECVParameters:
    min_features_to_select: int = 5
    n_jobs: int = -1
    scoring: str = "roc_auc"
    cv: int | None  = None

def _check_feature_selector(feature_selector):
    if feature_selector in ["forward", "backward", "rfecv"]:
        print(f"Feature selection process: {feature_selector}")
    else:
        NotImplemented(f"NOT Implemented Feature selection process: {feature_selector}")

def set_sequential_feature_selector(estimator, params: SequentialFeatureParameters) -> SequentialFeatureSelector:
    return SequentialFeatureSelector(
        estimator = estimator,
        n_features_to_select = params.n_features_to_select,
        direction = params.direction,
        scoring = params.scoring,
        tol = params.tol,
        cv = params.cv,
        n_jobs = params.n_jobs
        )

def set_rfecv_feature_selector(estimator, params: RFECVParameters) -> RFECV:
    return RFECV(
        estimator=estimator,
        scoring = params.scoring,
        cv = params.cv,
        n_jobs = params.n_jobs
        )


def set_feature_selection(
        estimator, 
        params: SequentialFeatureParameters | RFECVParameters
        ):

    direction = getattr(params, "direction", "rfecv")
    _check_feature_selector(direction)

    if direction == "rfecv":
        feature_selector = set_rfecv_feature_selector(
            estimator=estimator,
            params=params
        )
    else:
        feature_selector = set_sequential_feature_selector(
            estimator=estimator,
            params=params
        )

    return feature_selector

def load_transformed_data(path):
    # Load transformed data and return only cols with non singular value
    transformed_data = pd.read_parquet(path)
    # select_columns = transformed_data.columns[transformed_data.nunique() != 1]
    return transformed_data


def main(feature_selector=FEATURE_SELECTION_TYPE):
    print("===========================================================")
    print("==================Feature Selection========================")
    print("===========================================================")

    os.makedirs(path := dest_dir, exist_ok=True)
    print(f"Working dir is:  {path}")
    os.makedirs(os.path.join(path, feature_selector), exist_ok=True)
    # breakpoint()
    transformed_data = load_transformed_data(root_dir.joinpath("preprocessing", "transform-data.parquet"))
    # print(transformed_data.head())


    print("Using automatic bins")
    with open(
        file=f"{predecessor_dir}/selected-features-varclushi.json",
        mode="r",
        encoding="utf-8",
    ) as fh:
        ft = json.load(fh)
    features_ = ft["selected-features-varclushi"]

    logreg = LogisticRegression(max_iter=MAX_ITER_LOGREG)
    pipeline_params = RFECVParameters()
    

    feat_selection_pipeline = set_feature_selection(
        estimator=logreg,
        params=pipeline_params
    )
    feat_selection_pipeline.fit(
        X=transformed_data[features_],
        y=transformed_data[TARGET].astype("int8")
    )

    print(f"The number of features to select from is: {len(features_)}")

    selected_features_pl = list(feat_selection_pipeline.get_feature_names_out())

    print(f"The number of features selected is: {len(selected_features_pl)}")
    print(selected_features_pl)

    with open(
        file=f"{path}/selected-features-{feature_selector}.json",
        mode="w",
        encoding="utf-8",
    ) as f:
        json.dump(
            {f"selected-features-{feature_selector}": selected_features_pl}, f, indent=6
        )


if __name__ == "__main__":
    main()
