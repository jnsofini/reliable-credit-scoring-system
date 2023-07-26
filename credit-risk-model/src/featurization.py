import json
import os
import sys
import warnings

import config
import pandas as pd
from sklearn.feature_selection import RFECV, SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from util import setup_binning

warnings.filterwarnings("ignore", category=DeprecationWarning)


TARGET: str = "RiskPerformance"
TOP_FEATURE_NUM: int = 15
MAX_ITER_LOGREG: int = 1000
FEATURE_SELECTION_TYPE: str = "rfecv"


def feature_selection_pipeline(X, y, *, feature_selector="", is_binned=True):
    if feature_selector in ["forward", "backward", "rfe", "rfecv"]:
        print(f"Feature selection process: {feature_selector}")
    else:
        print(f"NOT Implemented Feature selection process: {feature_selector}")
        sys.exit()

    # if X.shape[1] > TOP_FEATURE_NUM:
    #     num_feat_to_select = TOP_FEATURE_NUM
    #     num_feat_to_select_rfe = TOP_FEATURE_NUM
    # else:
    #     num_feat_to_select = "auto"
    #     num_feat_to_select_rfe = None
    num_feat_to_select = "auto"

    if feature_selector in ["forward", "backward"]:
        feature_selection = SequentialFeatureSelector(
            LogisticRegression(max_iter=MAX_ITER_LOGREG),
            n_features_to_select=num_feat_to_select,
            direction=feature_selector,
            n_jobs=12,
            scoring="roc_auc",
            tol=-0.001,
        )
    else:
        # feature_selection = RFE(
        #             estimator=LogisticRegression(max_iter=MAX_ITER_LOGREG),
        #             n_features_to_select=num_feat_to_select_rfe
        #         )
        feature_selection = RFECV(
            LogisticRegression(max_iter=MAX_ITER_LOGREG),
            # n_features_to_select=num_feat_to_select_rfe,
            # min_features_to_select=8,
            cv=2,
            scoring="roc_auc",
            n_jobs=-1,
        )

    if is_binned:
        pipeline_ = feature_selection
        # return pipeline_.fit(X, y)
    else:
        pipeline_ = Pipeline(
            steps=[
                ("binning_process", setup_binning(X)),
                (
                    "feature_selection",
                    feature_selection,
                ),
            ]
        )
        #  pipeline_.fit(X, y)
        # returnpipeline_["feature_selection"]

    return pipeline_.fit(X, y)


def load_transformed_data(path):
    # Load transformed data and return only cols with non singular value
    transformed_data = pd.read_parquet(path)
    # select_columns = transformed_data.columns[transformed_data.nunique() != 1]
    return transformed_data


def filter_by_iv(df, *, iv_table, iv_cutoff=0.01):
    # iv_table = binning_obj.summary()
    columns_with_right_iv = iv_table[iv_table["iv"] > iv_cutoff]["name"].values
    return df[columns_with_right_iv]


def main(feature_selector=FEATURE_SELECTION_TYPE):
    print("===========================================================")
    print("==================Feature Selection========================")
    print("===========================================================")
    # Define base path
    # segment = "segments/non-rsps-features"
    # segment = "ALNC"
    # Define storage for data

    os.makedirs(path := config.BASE_PATH, exist_ok=True)
    print(f"Working dir is:  {path}")
    os.makedirs(os.path.join(path, feature_selector), exist_ok=True)
    # breakpoint()
    transformed_data = load_transformed_data(
        os.path.join(config.BASE_PATH, config.TRANSFORM_DATA_PATH)
    )
    # print(transformed_data.head())

    # with open(f"{path}/selected-features-varclushi.json") as fh:
    #     ft = json.load(fh)

    # Feed the selected features to RFE
    # feat_selection_pipeline = feature_selection_pipeline(
    #     X=transformed_data[ft["selected-features-varclushi"]],
    #     y=transformed_data[TARGET].astype("int8"),
    #     feature_selector=feature_selector
    # )

    print("Using automatic bins")
    with open(
        file=f"{path}/selected-features-varclushi.json",
        mode="r",
        encoding="utf-8",
    ) as fh:
        ft = json.load(fh)
    features_ = ft["selected-features-varclushi"]

    feat_selection_pipeline = feature_selection_pipeline(
        X=transformed_data[features_],
        y=transformed_data[TARGET].astype("int8"),
        feature_selector=feature_selector,
    )

    print(f"The number of features to select from is: {len(features_)}")

    if isinstance(feat_selection_pipeline, Pipeline):
        selected_features_pl = list(
            feat_selection_pipeline["feature_selection"].get_feature_names_out()
        )
    else:
        selected_features_pl = list(feat_selection_pipeline.get_feature_names_out())

    print(f"The number of features selected is: {len(selected_features_pl)}")
    print(selected_features_pl)

    with open(
        file=f"{path}/{feature_selector}/selected-features-{feature_selector}.json",
        mode="w",
        encoding="utf-8",
    ) as f:
        json.dump(
            {f"selected-features-{feature_selector}": selected_features_pl}, f, indent=6
        )


if __name__ == "__main__":
    main()
