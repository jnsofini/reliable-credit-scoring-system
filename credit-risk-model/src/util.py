import numpy as np
import pandas as pd
from optbinning import BinningProcess, Scorecard
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve

# from statsmodels.stats.outliers_influence import variance_inflation_factor
# from patsy import dmatrices

SPECIAL_CODES = [-9]
MISSING = [-99_000_000]


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


def setup_binning(df, *, target=None, features=None, binning_fit_params=None):
    """
    Setup the binning process for optbinning.

    Args:
        binning_fit_params: fit parameters object, including splits
        features: the list of features that we are interested in
        target: the target variable
        df (DataFrame): Dataframe containing features and a target column called 'target'

    Returns: Optbinning functional to bin the data BinningProcess()

    """
    # Remove target if present in data
    if target:
        df = df[list(set(df.columns.values) - {target})]

    # Subset only the features provided by user
    if features:
        binning_features = features
    else:
        binning_features = df.columns.values

    categorical_variables = _get_categorical_features(df[binning_features])

    return BinningProcess(
        categorical_variables=categorical_variables,
        variable_names=binning_features,
        # Uncomment the below line and pass a binning fit parameter
        # to stop doing automatic binning
        binning_fit_params=binning_fit_params,
        # This is the prebin size that should make the feature set usable
        min_prebin_size=10e-5,
        special_codes=SPECIAL_CODES,
    )


def _get_categorical_features(df):
    categorical_variables = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.values

    return categorical_variables

def _remove_feature(df: pd.DataFrame, columns_to_drop: str | list[str] | None = None):
    if columns_to_drop is None:
        return df
    if isinstance(columns_to_drop, str):
        columns_to_drop = [columns_to_drop]

    columns_to_drop = list(set(columns_to_drop).intersection(set(df.columns.values)))
    return df.drop(columns=columns_to_drop)

def _get_binning_features(df, *, target=None, features=None):
    """
    Setup the binning process for optbinning.

    Args:
        binning_fit_params: fit parameters object, including splits
        features: the list of features that we are interested in
        target: the target variable
        df (DataFrame): Dataframe containing features and a target column called 'target'

    Returns: Optbinning functional to bin the data BinningProcess()

    """
    # Remove target if present in data
    if target:
        df = _remove_feature(df=df, columns_to_drop=target)

    binning_features = features or df.columns.to_list()
    categorical_features = (
        df[binning_features]
        .select_dtypes(include=["object", "category", "string"])
        .columns.values
    )

    return binning_features, categorical_features


def get_best_feature_from_each_cluster(clusters):
    """The best feature from each cluster is selected.

      The best feature, defined as one with the min RS Ratio from that cluster.
      If the feature with the highest IV is different than the one with the
      highest RS Ratio, it is included as well.

    Args:
        clusters (pd.DataFrame): Table containing the clusters and characteristics

    Returns:
        List: List of selected features
    """
    highest_iv = clusters.loc[clusters.groupby(["Cluster"])["iv"].idxmax()][
        "Variable"
    ].tolist()
    lowest_rs_ratio = clusters.loc[clusters.groupby(["Cluster"])["RS_Ratio"].idxmin()][
        "Variable"
    ].tolist()

    return list(set(highest_iv + lowest_rs_ratio))


def get_iv_from_binning_obj(path):
    iv_table = BinningProcess.load(path).summary()
    iv_table["iv"] = iv_table["iv"].astype("float").round(3)
    return iv_table[["iv", "name", "n_bins"]]


def filter_iv_table(iv_table, iv_cutoff=0.02, min_n_bins=2):
    # Filter based on IV and min_number of bins
    return iv_table.query(f"n_bins >= {min_n_bins} and iv >= {iv_cutoff}").name.values


# def calculate_vif(data, features, target):
#     data = data[list(features) + [target]]
#     _, X = dmatrices(f"{target} ~" + "+".join(features), data, return_type="dataframe")
#     X = data[features].values

#     vif_info = pd.DataFrame()
#     vif_info["VIF"] = [variance_inflation_factor(X, i) for i in range(X.shape[1])]
#     vif_info["feature"] = features
#     vif_info.sort_values("VIF", ascending=False)
#     return vif_info


def scorecard(process, *, method=None):
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


def load_data(path, drop_cols=None):
    df = pd.read_parquet(path)
    if drop_cols:
        columns_to_drop = list(set(drop_cols).intersection(set(df.columns.values)))
        return df.drop(columns=columns_to_drop)
    return df


def sensivity_specifity_cutoff(y_true, y_score):
    '''Find data-driven cut-off for classification

    Cut-off is determied using Youden's index defined as sensitivity + specificity - 1.

    Parameters
    ----------

    y_true : array, shape = [n_samples]
        True binary labels.

    y_score : array, shape = [n_samples]
        Target scores, can either be probability estimates of the positive class,
        confidence values, or non-thresholded measure of decisions (as returned by
        “decision_function” on some classifiers).

    References
    ----------

    Ewald, B. (2006). Post hoc choice of cut points introduced bias to diagnostic research.
    Journal of clinical epidemiology, 59(8), 798-801.

    Steyerberg, E.W., Van Calster, B., & Pencina, M.J. (2011). Performance measures for
    prediction models and markers: evaluation of predictions and classifications.
    Revista Espanola de Cardiologia (English Edition), 64(9), 788-794.

    Jiménez-Valverde, A., & Lobo, J.M. (2007). Threshold criteria for conversion of probability
    of species presence to either–or presence–absence. Acta oecologica, 31(3), 361-369.
    '''
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    idx = np.argmax(tpr - fpr)
    return thresholds[idx]
