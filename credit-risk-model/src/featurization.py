""" 
Run from the credit-risk-model directory, with pipenv from reliable-credit-scoring-system
python -m src.featurization 
"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-few-public-methods

# import json
import logging as log
# import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import hydra
import pandas as pd
from omegaconf import DictConfig#, OmegaConf
from sklearn.feature_selection import RFECV, SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression
from src.tools import read_json, save_dict_to_json, stage_info, timeit

warnings.filterwarnings("ignore", category=DeprecationWarning)


# TARGET: str = "RiskPerformance"
# TOP_FEATURE_NUM: int = 15
# MAX_ITER_LOGREG: int = 1000
# FEATURE_SELECTION_TYPE: str = "rfecv"

# DATA_DIR = "data"
STAGE = "featurization"
# test_dir = 'dev-test'

# root_dir = Path(DATA_DIR).joinpath(test_dir)
# predecessor_dir = root_dir.joinpath("clustering")
# dest_dir = root_dir.joinpath(STAGE)

FILE_DIR = Path(__file__).parent

log.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=log.DEBUG)


@dataclass
class FeatureSelectionParameters: # pylint: disable=missing-class-docstring
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
class SequentialFeatureParameters: # pylint: disable=missing-class-docstring
    direction: Literal["forward", "backward"] = "forward"
    n_features_to_select: str | int = "auto"
    n_jobs: int = -1
    scoring: str = "roc_auc"
    tol: float = 1e-3
    cv: int | None = None #pylint: disable=invalid-name

    def __post_init__(self):
        if self.direction == "backward":
            self.tol = -1 * self.tol


class RFECVParameters: # pylint: disable=missing-class-docstring
    min_features_to_select: int = 5
    n_jobs: int = -1
    scoring: str = "roc_auc"
    cv: int | None = None


def _check_feature_selector(feature_selector):
    """Validate the feature selection process."""
    if feature_selector in ["forward", "backward", "rfecv"]:
        print(f"Feature selection process: {feature_selector}")
    else:
        raise NotImplementedError(f"NOT Implemented Feature selection process: {feature_selector}")


def set_sequential_feature_selector(
    estimator,
    params: SequentialFeatureParameters
    ) -> SequentialFeatureSelector:
    """Setup feature selection process."""
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
    """Setup recursive feature selection process."""
    return RFECV(
        estimator=estimator, scoring=params.scoring, cv=params.cv, n_jobs=params.n_jobs
    )


def set_feature_selection(
    estimator, params: SequentialFeatureParameters | RFECVParameters
):
    """Decide which direction feature selection process should follow."""
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


def set_destination_directory(cfg: DictConfig):
    """Prepares the directories.

    Args:
        cfg (DictConfig): Configuration data

    Returns:
        list[Path]: List of directories
    """
    root_dir = Path(cfg.data.source).joinpath(cfg.data.test_dir)
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


@timeit(log.info)
@hydra.main(version_base=None, config_path="..", config_name="params")
def main(cfg: DictConfig, feature_selector="rfecv"):
    """Main function that runs all processes."""
    log.debug(stage_info(stage=STAGE))

    predecessor_dir, destination_dir, root_dir = set_destination_directory(cfg=cfg)
    # log.debug(f"Working dir is:  {destination_dir}")
    # breakpoint()
    transformed_data = pd.read_parquet(
        root_dir.joinpath("preprocessing", "transform-data.parquet")
    )

    log.info("Using automatic bins")
    feature_selection_file = read_json(f"{predecessor_dir}/selected-features-varclushi.json")
    features_ = feature_selection_file["selected-features-varclushi"]

    logreg = LogisticRegression(max_iter=cfg.featurization.max_iter)
    pipeline_params = RFECVParameters()

    feat_selection_pipeline = set_feature_selection(
        estimator=logreg, params=pipeline_params
    )
    feat_selection_pipeline.fit(
        X=transformed_data[features_],
        y=transformed_data[cfg.data.target].astype("int8"),
    )

    log_feature_summary(
        features_in=len(features_),
        features_out=list(feat_selection_pipeline.get_feature_names_out()),
    )

    save_dict_to_json(
        data={
            f"selected-features-{feature_selector}": list(
                feat_selection_pipeline.get_feature_names_out()
            )
        },
        filename=f"{destination_dir}/selected-features-{feature_selector}.json",
    )


if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter
